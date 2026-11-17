import struct
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p,"rb").read()
for start, end in [(0xF93A0,0xF9410),(0xFA550,0xFA5C0)]:
    print("===", hex(start))
    for i in range(start, end, 4):
        w = struct.unpack_from("<I", d, i)[0]
        print("  ", hex(i), hex(w), w)
