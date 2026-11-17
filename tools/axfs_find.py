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
for i in range(0, 517):
    nm = inode_name(i)
    if nm in ("busybox","version.txt","ash","init","sh","mount"):
        print(i, repr(nm), oct(table("modes", table("inode_mode_index", i))), "size", table("inode_file_size", i), "entries", table("inode_num_entries", i), "aidx", table("inode_array_index", i))
