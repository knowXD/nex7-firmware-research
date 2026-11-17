import struct, zlib, os

IMG = "nex7/work_initrd.img"
OUT = "nex7/initrd_unpacked"
d = open(IMG, "rb").read()
be64 = lambda o: struct.unpack_from(">Q", d, o)[0]
NAMES = ["strings","xip","byte_aligned","compressed","node_type","node_index","cnode_offset","cnode_index","banode_offset","cblock_offset","inode_file_size","inode_name_offset","inode_num_entries","inode_mode_index","inode_array_index","modes","uids","gids"]
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
    out = bytearray()
    cache = {}
    for p in range(npages):
        ai = base + p
        node_index = table("node_index", ai)
        ntype = table("node_type", ai)
        if ntype == 1:
            cnode_offset = table("cnode_offset", node_index)
            cnode_index = table("cnode_index", node_index)
            if cnode_index not in cache:
                ofs = table("cblock_offset", cnode_index)
                end = table("cblock_offset", cnode_index+1)
                comp = d[reg["compressed"]["fsoff"]+ofs:reg["compressed"]["fsoff"]+end]
                cache[cnode_index] = zlib.decompress(comp)
            blk = cache[cnode_index]
            ln = min(PAGE - cnode_offset, PAGE)
            out += blk[cnode_offset:cnode_offset+ln]
        elif ntype == 2:
            ofs = table("banode_offset", node_index)
            out += d[reg["byte_aligned"]["fsoff"]+ofs : reg["byte_aligned"]["fsoff"]+ofs+PAGE]
        else:
            ofs = node_index*PAGE
            out += d[reg["xip"]["fsoff"]+ofs : reg["xip"]["fsoff"]+ofs+PAGE]
    return bytes(out[:size])

S_IFMT=0o170000; S_IFDIR=0o040000; S_IFREG=0o100000; S_IFLNK=0o120000
extracted = 0; links = 0; skipped = 0
manifest = []
def walk(ino, path):
    global extracted, links, skipped
    n = table("inode_num_entries", ino)
    base = table("inode_array_index", ino)
    for j in range(n):
        e = base + j
        name = inode_name(e)
        if name in (".",".."): continue
        mode = table("modes", table("inode_mode_index", e))
        full = os.path.join(path, name)
        t = mode & S_IFMT
        if t == S_IFDIR:
            os.makedirs(full, exist_ok=True)
            walk(e, full)
        elif t == S_IFREG:
            data = read_file(e)
            os.makedirs(os.path.dirname(full), exist_ok=True)
            with open(full, "wb") as f: f.write(data)
            extracted += 1
        elif t == S_IFLNK:
            tgt = read_file(e).decode("latin1")
            try:
                os.symlink(tgt, full)
            except Exception:
                with open(full, "w") as f: f.write(tgt)
            links += 1
        else:
            # 设备节点/管道：Windows 没法 mknod，记成清单，别静默丢掉
            skipped += 1
            rdev = table("inode_file_size", e)
            kind = {0o020000: "chr", 0o060000: "blk", 0o010000: "fifo"}.get(t, oct(t))
            manifest.append("%s,%s,%04o,%d,%d" % (full, kind, mode & 0o7777, (rdev >> 8) & 0xff, rdev & 0xff))

os.makedirs(OUT, exist_ok=True)
walk(0, OUT)
print("extracted files", extracted, "symlinks", links, "special skipped", skipped)
with open(os.path.join(OUT, "dev_nodes.txt"), "w", encoding="utf-8") as f:
    f.write("# path,type,perm,major,minor" + chr(10))
    f.write(chr(10).join(manifest) + chr(10))
print("设备/管道清单写到", os.path.join(OUT, "dev_nodes.txt"), len(manifest), "条")
