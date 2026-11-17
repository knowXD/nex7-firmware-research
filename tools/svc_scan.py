import struct
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p,"rb").read()
# count ARM svc instructions (word & 0xFF000000 == 0xEF000000)
n = 0; samples = []
for i in range(0, len(d)-4, 4):
    w = struct.unpack_from("<I", d, i)[0]
    if (w & 0xFF000000) == 0xEF000000:
        n += 1
        if len(samples) < 10: samples.append((i, w & 0xFFFFFF))
print("ARM svc count", n)
print("samples", [(hex(o), hex(imm)) for o, imm in samples])
# Thumb svc: 0xDFxx (16-bit)
n2 = 0; s2 = []
for i in range(0, len(d)-2, 2):
    w = struct.unpack_from("<H", d, i)[0]
    if (w & 0xFF00) == 0xDF00:
        n2 += 1
        if len(s2) < 10: s2.append((i, w & 0xFF))
print("Thumb svc count", n2)
print("samples", [(hex(o), hex(imm)) for o, imm in s2])
