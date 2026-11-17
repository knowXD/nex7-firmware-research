import struct
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p,"rb").read()
base = 0xC3421000
for i in range(8):
    off = 0x475E7C + i*16
    vals = struct.unpack_from("<IIII", d, off)
    print("entry", i, [hex(v) if v > 0xFFFF else v for v in vals])
# also check the 24M literal use at 0xf97e0 done earlier
