import struct
d = open("nex7/work_initrd.img","rb").read()
be32 = lambda o: struct.unpack_from(">I", d, o)[0]
be64 = lambda o: struct.unpack_from(">Q", d, o)[0]
magic = be32(0)
sig = d[4:20]
digest = d[20:60]
cblock = be32(60)
files = be64(64)
size = be64(72)
blocks = be64(80)
mmap_size = be64(88)
regions = []
names = ["strings","xip","byte_aligned","compressed","node_type","node_index","cnode_offset","cnode_index","banode_offset","cblock_offset","inode_file_size","inode_name_offset","inode_num_entries","inode_mode_index","inode_array_index","modes","uids","gids"]
for i, n in enumerate(names):
    regions.append((n, be64(96 + i*8)))
off = 96 + len(names)*8
ver = (d[off], d[off+1], d[off+2])
comp = d[off+3]
ts = be64(off+4)
page_shift = d[off+12]
print("magic %08x" % magic, "sig", sig)
print("cblock", cblock, "files", files, "size", size, "blocks", blocks, "mmap", mmap_size)
for n, o in regions:
    print("  region", n, hex(o))
print("version", ver, "compression", comp, "timestamp", ts, "page_shift", page_shift)
