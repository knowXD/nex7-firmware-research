import re
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p, "rb").read()
def dump(center, span=0x1400):
    s = max(0, center-span); e = min(len(d), center+span)
    print("=== 0x%06X ±0x%X ===" % (center, span))
    for m in re.finditer(rb"[ -~]{6,}", d[s:e]):
        print("   0x%06X %s" % (s+m.start(), m.group().decode("latin1")[:100]))
dump(0x0F4174, 0x1000)
