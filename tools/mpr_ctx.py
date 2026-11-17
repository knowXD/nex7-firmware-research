import re, struct
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/lib/libmpr.so"
d = open(p, "rb").read()
print("libmpr.so size", len(d))
off = 0x4ED990
print("\n== 0x%X 附近 96 字节 ==" % off)
seg = d[off-48:off+96]
print(" ".join("%02x" % b for b in seg))
print("\n== 附近字符串（±6KB） ==")
start = max(0, off-0x1800); end = min(len(d), off+0x1800)
for m in re.finditer(rb"[ -~]{5,}", d[start:end]):
    pos = start + m.start()
    print("   0x%06X %s" % (pos, m.group().decode("latin1")[:100]))
