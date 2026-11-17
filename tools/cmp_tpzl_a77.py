import sys, struct, io
sys.path.append("nex7/pylibs"); sys.path.append("nex7/fwtool.py-master")
from fwtool.lz77 import inflateLz77
for ver, p in [("NEX-7","nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3"),
               ("A77","nex7/a77/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3")]:
    d = open(p,"rb").read()
    magic, bs, tocoff, tocsz = struct.unpack_from("<4sIII", d, 0)
    n = tocsz//8
    off,size = struct.unpack_from("<II", d, tocoff)
    b = io.BytesIO(d[off:off+size]); read=0; chunks=[]
    while read < (1<<bs):
        c = len(inflateLz77(b)); chunks.append(c); read += c
        if len(chunks) > 32: break
    print(ver, "img", len(d), "bs", bs, "blocks", n, "block0 chunks", chunks[:4], "count", len(chunks))
    av = open(p + "_unpacked_unpacked/av-cam.bin","rb").read(16)
    print("   av-cam head", av.hex(" "))
