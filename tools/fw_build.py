#!/usr/bin/env python3
"""Patch a Sony firmware.tar: in-place byte patches and/or member replacement."""
import argparse, json, os, sys, tarfile, zlib, io

NL = chr(10)
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fwtool.py-master"))

def tpzl_structure(data):
    """Return (blockSize, tocOffset, tocSize, nblocks, [chunk lengths per block]) or None."""
    if data[:4] != b"TPZL":
        return None
    import struct
    from fwtool.lz77 import inflateLz77
    magic, bs, tocoff, tocsz = struct.unpack_from("<4sIII", data, 0)
    n = tocsz // 8
    blocks = []
    for i in range(n):
        off, size = struct.unpack_from("<II", data, tocoff + i * 8)
        b = io.BytesIO(data[off:off + size])
        read = 0; chunks = []
        while read < (1 << bs):
            c = len(inflateLz77(b))
            chunks.append(c); read += c
            if len(chunks) > 256:
                break
        blocks.append(tuple(chunks))
    return (bs, tocoff, tocsz, n, blocks)

def verify_structures(new_tar_data, ref_tar_path, names):
    """Compare TPZL structure of replaced members against a reference tar."""
    ref = tarfile.open(ref_tar_path, "r:")
    ref_members = {m.name: m for m in ref.getmembers()}
    ok = True
    for name in names:
        with tarfile.open(fileobj=io.BytesIO(new_tar_data), mode="r:") as nt:
            new_blob = nt.extractfile(nt.getmember(name)).read()
        if name not in ref_members:
            print("verify: %s not in reference, skipped" % name)
            continue
        ref_blob = ref.extractfile(ref_members[name]).read()
        a = tpzl_structure(new_blob); b = tpzl_structure(ref_blob)
        if a is None or b is None:
            print("verify: %s is not TPZL, skipped" % name)
            continue
        if a[0:4] != b[0:4] or a[4] != b[4]:
            ok = False
            print("VERIFY FAILED: %s structure mismatch" % name)
            if a[0:4] != b[0:4]:
                print("  header new", a[0:4], "ref", b[0:4])
            for i, (ca, cb) in enumerate(zip(a[4], b[4])):
                if ca != cb:
                    print("  block %d: new %s vs ref %s" % (i, ca[:6], cb[:6]))
                    break
        else:
            print("verify: %s structure OK (%d blocks, %d segs/block)" % (name, a[3], len(a[4][0]) if a[4] else 0))
    ref.close()
    return ok

def load_members(path):
    tf = tarfile.open(path, "r:")
    return tf, [m for m in tf.getmembers()]

def find_sum_line(text, member):
    base = member.split("/")[-1]
    lines = text.split(NL)
    for i, line in enumerate(lines):
        p = line.split(",")
        if len(p) > 10 and p[-2].endswith(base):
            return i, p
    return None, None

def update_sum_for(data, members, name, crc, size):
    for sm in members:
        if not sm.name.endswith(".sum"):
            continue
        off = sm.offset_data
        text = bytes(data[off:off + sm.size]).decode("latin1")
        idx, p = find_sum_line(text, name)
        if p is None:
            continue
        lines = text.split(NL)
        p[1] = "%08x" % crc
        p[2] = "%08x" % size
        lines[idx] = ",".join(p)
        new = NL.join(lines).encode("latin1")
        if len(new) != sm.size:
            sys.exit("sum size changed for " + sm.name)
        data[off:off + sm.size] = new
        return True
    return False

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--patch")
    ap.add_argument("--replace-member", action="append", default=[])
    ap.add_argument("--pack")
    ap.add_argument("--verify-against")
    ap.add_argument("--config")
    ap.add_argument("--updater")
    args = ap.parse_args()

    tf, members = load_members(args.src)
    data = bytearray(open(args.src, "rb").read())
    changed = set()

    if args.patch:
        for p in json.load(open(args.patch)):
            name, off, blob = p["file"], int(p["offset"]), bytes.fromhex(p["hex"])
            m = [x for x in members if x.name == name][0]
            data[m.offset_data + off: m.offset_data + off + len(blob)] = blob
            changed.add(name)

    replaces = {}
    for spec in args.replace_member:
        name, path = spec.split("=", 1)
        replaces[name] = open(path, "rb").read()

    if replaces:
        buf = io.BytesIO()
        with tarfile.open(fileobj=buf, mode="w", format=tarfile.USTAR_FORMAT) as out:
            for m in members:
                if m.name in replaces:
                    blob = replaces[m.name]
                    m2 = tarfile.TarInfo(m.name)
                    m2.size = len(blob); m2.mode = m.mode; m2.mtime = m.mtime
                    m2.uid = m.uid; m2.gid = m.gid; m2.uname = m.uname; m2.gname = m.gname
                    out.addfile(m2, io.BytesIO(blob))
                elif m.isdir():
                    out.addfile(m, None)
                else:
                    out.addfile(m, tf.extractfile(m))
        data = bytearray(buf.getvalue())
        tmp = args.out + ".tmp"
        open(tmp, "wb").write(data)
        tf2 = tarfile.open(tmp, "r:")
        members2 = list(tf2.getmembers())
        tf2.close()
        os.remove(tmp)
        for name, blob in replaces.items():
            crc = zlib.crc32(blob) & 0xffffffff
            if not update_sum_for(data, members2, name, crc, len(blob)):
                sys.exit("no sum line for " + name)
            changed.add(name)
    elif args.patch:
        for name in changed:
            m = [x for x in members if x.name == name][0]
            blob = bytes(data[m.offset_data:m.offset_data + m.size])
            update_sum_for(data, members, name, zlib.crc32(blob) & 0xffffffff, m.size)

    if replaces:
        ref = args.verify_against or args.src
        if not verify_structures(bytes(data), ref, list(replaces)):
            sys.exit("structure verification failed, output not written")

    open(args.out, "wb").write(data)
    print("wrote %s (%d bytes), changed %d member(s)" % (args.out, len(data), len(changed)))

    if args.pack:
        if not args.config or not args.updater:
            sys.exit("--pack needs --config and --updater")
        os.makedirs(args.pack, exist_ok=True)
        cmd = " ".join([sys.executable, "nex7/fwtool.py-master/fwtool.py", "pack",
                        "-c", args.config, "-u", args.updater, "-f", args.out, "-o", args.pack])
        print(cmd)
        os.system(cmd)

if __name__ == "__main__":
    main()
