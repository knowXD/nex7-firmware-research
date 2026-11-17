import struct
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p,"rb").read()
w = struct.unpack_from("<I", d, 0x6D1A0)[0]
print("literal at 0x6D1A0:", hex(w), struct.unpack("<f", struct.pack("<I", w))[0])
# find refs to literal address 0x6D1A0 (file offset); code loads it via pc-relative ldr
import re
# search for 4-byte little-endian 0xA0D10600? no; ldr literal uses immediate offset from pc.
# Instead scan instructions? Simple: look for the literal pattern 00 00 c8 42 nearby and count.
pat = struct.pack("<I", 0x42C80000)
hits = []
i = d.find(pat)
while i >= 0 and len(hits) < 20:
    hits.append(i); i = d.find(pat, i+1)
print("0x42C80000 occurrences:", [hex(h) for h in hits])
