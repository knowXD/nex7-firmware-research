import struct, zlib, sys
IMG = "nex7/work_initrd.img"
d = open(IMG, "rb").read()
be64 = lambda o: struct.unpack_from(">Q", d, o)[0]
NAMES = ["strings","xip","byte_aligned","compressed","node_type","node_index","cnode_offset",
         "cnode_index","banode_offset","cblock_offset","inode_file_size","inode_name_offset",
         "inode_num_entries","inode_mode_index","inode_array_index","modes","uids","gids"]
reg = {}
for i, n in enumerate(NAMES):
    off = be64(96 + i*8)
    fsoff, size, csize, maxi = struct.unpack_from(">QQQQ", d, off)
    reg[n] = dict(fsoff=fsoff, size=size, max_index=maxi, depth=d[off+32])
def table(name, idx):
    r = reg[name]; dep = r["depth"]; n = r["max_index"]
    val = 0
    for k in range(dep):
        val |= d[r["fsoff"] + k*n + idx] << (8*k)
    return val
def inode_name(i):
    off = table("inode_name_offset", i)
    base = reg["strings"]["fsoff"] + off
    end = d.find(b"\x00", base)
    return d[base:end].decode("latin1")
PAGE = 4096
def read_file(i):
    size = table("inode_file_size", i)
    if size == 0: return b""
    npages = (size + PAGE - 1)//PAGE
    base = table("inode_array_index", i)
    out = bytearray(); cache = {}
    for p in range(npages):
        ai = base + p
        ni = table("node_index", ai); ntype = table("node_type", ai)
        if ntype == 1:
            co = table("cnode_offset", ni); ci = table("cnode_index", ni)
            if ci not in cache:
                ofs = table("cblock_offset", ci); end = table("cblock_offset", ci+1)
                cache[ci] = zlib.decompress(d[reg["compressed"]["fsoff"]+ofs:reg["compressed"]["fsoff"]+end])
            blk = cache[ci]; out += blk[co:co+PAGE]
        elif ntype == 2:
            ofs = table("banode_offset", ni)
            out += d[reg["byte_aligned"]["fsoff"]+ofs: reg["byte_aligned"]["fsoff"]+ofs+PAGE]
        else:
            ofs = ni*PAGE
            out += d[reg["xip"]["fsoff"]+ofs: reg["xip"]["fsoff"]+ofs+PAGE]
    return bytes(out[:size])
S_IFMT=0o170000; S_IFDIR=0o040000; S_IFREG=0o100000; S_IFLNK=0o120000; S_IFCHR=0o020000; S_IFBLK=0o060000
rows = []
def walk(ino, path):
    n = table("inode_num_entries", ino); base = table("inode_array_index", ino)
    for j in range(n):
        e = base + j
        nm = inode_name(e)
        if nm in (".", ".."): continue
        mode = table("modes", table("inode_mode_index", e)); t = mode & S_IFMT
        full = path + "/" + nm
        rows.append((full, t, mode & 0o7777, table("inode_file_size", e), e))
        if t == S_IFDIR: walk(e, full)
walk(0, "")
print("== /dev 里所有 tty* / console / null / zero ==")
for full, t, perm, size, e in rows:
    nm = full.rsplit("/",1)[-1]
    if nm.startswith("tty") or nm in ("console","null","zero","random","urandom"):
        if t == S_IFLNK:
            tgt = read_file(e).decode("latin1")
            print("  %-20s lnk  -> %s" % (full, tgt))
        else:
            major, minor = (size >> 8) & 0xff, size & 0xff
            kind = "chr" if t == S_IFCHR else ("blk" if t == S_IFBLK else oct(t))
            print("  %-20s %-4s %04o  dev=%d:%d  (rdev=0x%X)" % (full, kind, perm, major, minor, size))
