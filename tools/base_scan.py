import struct
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p,"rb").read()
targets = {"InvalidJpegQuality":0x2F324E, "encodeQuality":0x1E9BF7, "qscale":0x46114F, "TskAvifVSync":0x1080}
for name, off in targets.items():
    print("==", name, hex(off))
    hits = []
    for i in range(0, len(d)-4, 4):
        w = struct.unpack_from("<I", d, i)[0]
        if 0xC0000000 <= w <= 0xC4000000:
            base = w - off
            if 0xC0000000 <= base <= 0xC4000000 and (base & 0xFFF) == 0:
                hits.append((hex(i), hex(w), hex(base)))
    for h in hits[:10]:
        print("   ref", h)
    print("   total", len(hits))
