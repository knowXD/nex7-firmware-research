import struct
d = open("nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked","rb").read()
# first nonzero
for i in range(0, len(d), 4096):
    if any(d[i:i+16]):
        print("first nonzero block at", hex(i), d[i:i+32].hex())
        break
# search ext2 magic EF 53 preceded by plausible sb
import re
hits = [m.start() for m in re.finditer(b"\xef\x53", d)]
print("EF53 hits", len(hits), [hex(h) for h in hits[:10]])
# search known strings from the fs
for s in [b"AVBB_SCN_START_VIDEO.so", b"libObj.so", b"scenario"]:
    i = d.find(s)
    print(s, hex(i) if i>=0 else None)
