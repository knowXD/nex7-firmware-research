import sys, io, hashlib
sys.path.append("nex7/fwtool.py-master")
from fwtool.archive import lzpt
uf = next(lzpt.readLzpt(open("nex7/nflasha3_jpeg_all.tpzl","rb")))
d = uf.contents.read()
src = open("nex7/work_fat_jpeg_all.img","rb").read()
print("roundtrip", d == src, len(d))
for off in [0x461092,0x500464,0x555d64]:
    fat_off = 0x8E00 + off
    print(hex(off), "fat", hex(fat_off), list(src[fat_off:fat_off+8]))
