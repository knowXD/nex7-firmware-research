import struct, re
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/lib/libmpr.so"
d = open(p,"rb").read()
for name, val in [("1790",1790),("1800",1800),("1770",1770),("29min",1740),("1500",1500),("3000",3000)]:
    pat = struct.pack("<I", val)
    hits = []
    i = d.find(pat)
    while i >= 0 and len(hits) < 5:
        hits.append(i); i = d.find(pat, i+1)
    print(name, "hits", [hex(h) for h in hits])
# show strings around REC_LIMIT
i = d.find(b"REC_LIMIT_TIME")
print("REC_LIMIT_TIME at", hex(i))
seg = d[i-200:i+400]
for m in re.finditer(rb"[\x20-\x7e]{6,}", seg):
    print("  str", hex(i-200+m.start()), m.group().decode("latin1")[:100])
