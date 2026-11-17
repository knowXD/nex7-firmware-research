import struct
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p,"rb").read()
tab = d[0x461092:0x461092+128]
print("base table first16", list(tab[:16]))
# occurrences of the 128-byte table
hits = []
i = d.find(tab)
while i >= 0:
    hits.append(i); i = d.find(tab, i+1)
print("128B table occurrences", [hex(h) for h in hits])
# occurrences of the first 16 bytes (partial copies)
hits2 = []
i = d.find(tab[:16])
while i >= 0 and len(hits2) < 20:
    hits2.append(i); i = d.find(tab[:16], i+1)
print("first16 occurrences", [hex(h) for h in hits2])
# observed output tables from JPEG (zigzag order)
std = bytes([2,2,2,4,4,8,10,14])
fine = bytes([1,1,1,2,2,4,5,7])
for name, pat in [("std8", std), ("fine8", fine)]:
    hs = []
    i = d.find(pat)
    while i >= 0 and len(hs) < 10:
        hs.append(i); i = d.find(pat, i+1)
    print(name, [hex(h) for h in hs])
