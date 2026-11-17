import re
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p, "rb").read()
lo, hi = 0x0D9000, 0x0DA400
print("=== ENCMODEMGR 命令表区域 0x%X-0x%X ===" % (lo, hi))
for m in re.finditer(rb"[ -~]{6,}", d[lo:hi]):
    print("   0x%06X %s" % (lo+m.start(), m.group().decode("latin1")[:90]))
