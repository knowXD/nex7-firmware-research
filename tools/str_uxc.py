import struct
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/share/app/string_english.uxc"
d = open(p,"rb").read()
print("size", len(d))
for i in range(0, 0x80, 16):
    chunk = d[i:i+16]
    print("  %04x" % i, " ".join("%02x" % b for b in chunk), "".join(chr(b) if 32<=b<127 else "." for b in chunk))
# where is "HDMI Resolution"
i = d.find(b"HDMI Resolution")
print("HDMI Resolution at", hex(i))
# find references: 4-byte or 2-byte values equal to i
for width, fmt in [(2,"<H"),(4,"<I")]:
    pat = struct.pack(fmt, i)
    hits = []
    j = d.find(pat)
    while j >= 0 and len(hits) < 5:
        hits.append(j); j = d.find(pat, j+1)
    print("refs width", width, [hex(h) for h in hits])
