import struct
d = open("nex7/work_initrd.img","rb").read()
for off in [0xF4, 0x118, 0x25C, 0x280]:
    print("desc at", hex(off), d[off:off+36].hex())
print("bytes at 0x34F8:", d[0x34F8:0x34F8+32].hex())
print("bytes at 0x3D0C:", d[0x3D0C:0x3D0C+32].hex())
