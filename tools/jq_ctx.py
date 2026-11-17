import re, struct
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p,"rb").read()
seg = d[0x4610f0:0x461400]
print("strings around 0x46114f:")
for m in re.finditer(rb"[\x20-\x7e]{4,}", seg):
    print("  ", hex(0x4610f0+m.start()), m.group().decode("latin1")[:100])
print("--- pointer candidates ---")
for i in range(0, len(d)-4, 4):
    w = struct.unpack_from("<I", d, i)[0]
    if 0xC3000000 <= w <= 0xC4000000:
        base = w - 0x46114F
        if 0xC3000000 <= base <= 0xC3C00000 and (base & 0xFFFF) == 0:
            print(hex(i), hex(w), "base", hex(base))
