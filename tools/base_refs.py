import struct
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p,"rb").read()
base = 0xC3421000
targets = {"InvalidJpegQuality":0x2F324E, "encodeQuality":0x1E9BF7, "qscale":0x46114F,
           "quant_table":0x461092, "table_copy1":0x500464, "table_copy6":0x555D64}
for name, off in targets.items():
    w = base + off
    needle = struct.pack("<I", w)
    hits = []
    i = d.find(needle)
    while i >= 0 and len(hits) < 12:
        hits.append(i); i = d.find(needle, i+1)
    print(name, hex(w), "refs", [hex(h) for h in hits])
