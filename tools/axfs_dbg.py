import struct
d = open("nex7/work_initrd.img","rb").read()
be64 = lambda o: struct.unpack_from(">Q", d, o)[0]
NAMES = ["strings","xip","byte_aligned","compressed","node_type","node_index","cnode_offset","cnode_index","banode_offset","cblock_offset","inode_file_size","inode_name_offset","inode_num_entries","inode_mode_index","inode_array_index","modes","uids","gids"]
reg = {}
for i, n in enumerate(NAMES):
    off = be64(96 + i*8)
    fsoff, size, csize, maxi = struct.unpack_from(">QQQQ", d, off)
    reg[n] = dict(fsoff=fsoff, size=size, depth=d[off+32])
for n in ["inode_file_size","inode_name_offset","inode_num_entries","inode_mode_index","inode_array_index","modes"]:
    r = reg[n]
    base = r["fsoff"]
    vals = [struct.unpack_from(">I", d, base+4*k)[0] for k in range(6)]
    print(n, "fsoff", hex(base), "size", r["size"], "values", vals)
