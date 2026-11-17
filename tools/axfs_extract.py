import struct, zlib, os, sys

IMG = "nex7/work_initrd.img"
OUT = "nex7/initrd_unpacked"
d = open(IMG, "rb").read()

be32 = lambda o: struct.unpack_from(">I", d, o)[0]
be64 = lambda o: struct.unpack_from(">Q", d, o)[0]

NAMES = ["strings","xip","byte_aligned","compressed","node_type","node_index","cnode_offset","cnode_index","banode_offset","cblock_offset","inode_file_size","inode_name_offset","inode_num_entries","inode_mode_index","inode_array_index","modes","uids","gids"]
reg = {}
for i, n in enumerate(NAMES):
    off = be64(96 + i*8)
    fsoff, size, csize, maxi = struct.unpack_from(">QQQQ", d, off)
    depth, incore = d[off+32], d[off+33]
    reg[n] = dict(fsoff=fsoff, size=size, csize=csize, max_index=maxi, depth=depth)

def table(region, idx, depth=None):
    r = reg[region]
    dep = depth or r["depth"]
    base = r["fsoff"] + idx*dep
    val = 0
    for k in range(dep):
        val = (val << 8) | d[base+k]
    return val

def inode_size(i): return table("inode_file_size", i)
def inode_name_off(i): return table("inode_name_offset", i)
def inode_num(i): return table("inode_num_entries", i)
def inode_mode(i): return table("modes", table("inode_mode_index", i))
def inode_array(i): return table("inode_array_index", i)

def inode_name(i):
    off = inode_name_off(i)
    base = reg["strings"]["fsoff"] + off
    end = d.find(b"\x00", base)
    return d[base:end].decode("latin1")

def read_file(i):
    size = inode_size(i)
    if size == 0: return b""
    npages = (size + 4095)//4096
    base = inode_array(i)
    out = bytearray()
    cblk_cache = {}
    for p in range(npages):
        ai = base + p
        node_index = table("node_index", ai)
        ntype = table("node_type", ai)
        if ntype == 1:  # Compressed
            cnode_offset = table("cnode_offset", node_index)
            cnode_index = table("cnode_index", node_index)
            if cnode_index not in cblk_cache:
                ofs = table("cblock_offset", cnode_index)
                end = table("cblock_offset", cnode_index+1)
                comp = d[reg["compressed"]["fsoff"]+ofs : reg["compressed"]["fsoff"]+end]
                cblk_cache[cnode_index] = zlib.decompress(comp)
            blk = cblk_cache[cnode_index]
            ln = min(4096 - cnode_offset, 4096)
            out += blk[cnode_offset:cnode_offset+ln]
        elif ntype == 2:  # Byte_Aligned
            ofs = table("banode_offset", node_index)
            out += d[reg["byte_aligned"]["fsoff"]+ofs : reg["byte_aligned"]["fsoff"]+ofs+4096]
        else:  # XIP
            ofs = node_index*4096
            out += d[reg["xip"]["fsoff"]+ofs : reg["xip"]["fsoff"]+ofs+4096]
    return bytes(out[:size])

# sanity: version.txt
print("files", be64(64))
for i in range(0, 8):
    print(i, inode_name(i), oct(inode_mode(i)), inode_size(i))
