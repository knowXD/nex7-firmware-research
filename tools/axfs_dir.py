import struct
d = open("nex7/work_initrd.img","rb").read()
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
for dirino in [0, 2]:
    n = table("inode_num_entries", dirino)
    base = table("inode_array_index", dirino)
    print("dir", dirino, inode_name(dirino), "entries", n, "base", base)
    for j in range(min(n, 8)):
        e = base + j
        print("   entry", e, repr(inode_name(e)))
