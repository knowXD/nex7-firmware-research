import re, struct
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p, "rb").read()
off = 0x31e71c
print("=== 0x%X 附近字符串 ===" % off)
for m in re.finditer(rb"[ -~]{4,}", d[off-0x400: off+0x800]):
    print("   0x%06X %s" % (off-0x400+m.start(), m.group().decode("latin1")[:80]))

print("\n=== 附近像 9 个一组的数值（int16/float）===")
def show(off2, kind):
    try:
        if kind == "i16":
            vals = struct.unpack_from("<9h", d, off2)
        else:
            vals = struct.unpack_from("<9f", d, off2)
    except Exception:
        return
    if kind == "f":
        ok = all(-4 < v < 4 for v in vals)
    else:
        ok = all(-20000 < v < 20000 for v in vals)
    if ok:
        print("   0x%06X %s %s" % (off2, kind, ["%.3f" % v for v in vals] if kind=="f" else list(vals)))

for base in range(off-0x800, off+0x800, 2):
    show(base, "i16")
