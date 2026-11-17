d = open("nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked","rb").read()
import os
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/scenario/AVBB_SCN_START_VIDEO.so"
f = open(p,"rb").read()
print("so size", len(f))
# search for first 64 bytes
needle = f[:64]
hits = []
i = d.find(needle)
while i >= 0 and len(hits) < 5:
    hits.append(i); i = d.find(needle, i+1)
print("hits", [hex(h) for h in hits])
# verify full file at first hit
for h in hits[:1]:
    print("full match", d[h:h+len(f)] == f)
