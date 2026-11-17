import re
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p, "rb").read()
pats = re.compile(rb"[ -~]{5,}")
kw = re.compile(r"qscale|QP|Quant|VBR|CBR|BitRate|bitrate|RateCtrl|rate control|RC_|target.*rate|AVC_?BR", re.I)
print("== 与码率/量化相关的字符串 ==")
seen = set()
for m in pats.finditer(d):
    s = m.group().decode("latin1")
    if kw.search(s) and s not in seen:
        seen.add(s)
        print("   0x%06X %s" % (m.start(), s[:100]))
print("\n== 0x6D032 附近 ==")
off = 0x6D032
print(" ".join("%02x" % b for b in d[off-32:off+32]))
for m in pats.finditer(d[off-400:off+400]):
    print("   0x%06X %s" % (off-400+m.start(), m.group().decode("latin1")[:90]))
