import struct
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p,"rb").read()
for name, off in {"InvalidJpegQuality":0x2F324E, "encodeQuality":0x1E9BF7, "qscale":0x46114F, "quanttable":0x461092}.items():
    needle = struct.pack("<I", off)
    hits = []
    i = d.find(needle)
    while i >= 0 and len(hits) < 8:
        hits.append(hex(i)); i = d.find(needle, i+1)
    print(name, hex(off), "plain-refs", hits)
