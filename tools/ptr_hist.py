import struct
from collections import Counter
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p,"rb").read()
c = Counter()
for i in range(0, len(d)-4, 4):
    w = struct.unpack_from("<I", d, i)[0]
    if 0xC3000000 <= w <= 0xC3FFFFFF:
        c[w >> 20] += 1
for k, v in sorted(c.items(), key=lambda x: -x[1])[:15]:
    print(hex(k << 20), v)
