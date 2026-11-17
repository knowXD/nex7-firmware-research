import re
def ctx(path, kw, span=160, maxn=3):
    d = open(path, "rb").read()
    print("\n== %s : %r ==" % (path.split("\\")[-1], kw))
    n = 0
    for m in re.finditer(re.escape(kw), d):
        s = d[max(0, m.start()-span): m.start()+span]
        txt = "".join(chr(b) if 32 <= b < 127 else " " for b in s)
        print("  0x%06X %s" % (m.start(), re.sub(r"\s+", " ", txt)))
        n += 1
        if n >= maxn: break

base = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/"
ctx(base + "share/app/string_english.uxc", b"Interval", 200, 3)
ctx(base + "lib/libObj.so", b"INTERVAL", 140, 4)
ctx(base + "lib/libmpr.so", b"INTERVAL", 120, 2)
