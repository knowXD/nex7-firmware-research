import re
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/share/app/string_english.uxc"
d = open(p, "rb").read()
for kw in [b"Self-timer", b"Self timer", b"Self-Timer", b"Cont.", b"Drive Mode", b"Bracket"]:
    n = d.count(kw)
    i = d.find(kw)
    print("%-12s x%d %s" % (kw.decode(), n, ""))
    if i >= 0:
        s = d[max(0,i-120): i+160]
        print("    ", re.sub(r"\s+", " ", "".join(chr(b) if 32 <= b < 127 else " " for b in s)))
