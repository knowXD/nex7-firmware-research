import struct
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked"
d = open(p,"rb").read()
pat = struct.pack("<III", 28000000, 24000000, 18000000)
hits = []
i = d.find(pat)
while i >= 0:
    hits.append(i); i = d.find(pat, i+1)
print("pattern hits", [hex(h) for h in hits])
for h in hits:
    print(hex(h), list(struct.unpack_from("<IIIIII", d, h-8)))
