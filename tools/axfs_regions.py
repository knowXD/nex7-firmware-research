import struct
d = open("nex7/work_initrd.img","rb").read()
names = ["strings","xip","byte_aligned","compressed","node_type","node_index","cnode_offset","cnode_index","banode_offset","cblock_offset","inode_file_size","inode_name_offset","inode_num_entries","inode_mode_index","inode_array_index","modes","uids","gids"]
reg = {}
for i, n in enumerate(names):
    off = struct.unpack_from(">Q", d, 96 + i*8)[0]
    fsoff, size, csize, maxi = struct.unpack_from(">QQQQ", d, off)
    depth, incore = d[off+32], d[off+33]
    reg[n] = dict(fsoffset=fsoff, size=size, csize=csize, max_index=maxi, depth=depth, incore=incore)
for n in names:
    r = reg[n]
    print("%-18s off=%08x size=%-8d csize=%-8d max=%-6d depth=%d incore=%d" % (n, r["fsoffset"], r["size"], r["csize"], r["max_index"], r["depth"], r["incore"]))
# strings region content
s = reg["strings"]
blob = d[s["fsoffset"]:s["fsoffset"]+s["size"]]
parts = blob.split(b"\x00")
print("strings count", len(parts))
for p in parts[:25]:
    print("  ", p)
