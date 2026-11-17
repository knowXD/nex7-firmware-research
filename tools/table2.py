import struct
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p,"rb").read()
for start in [0x2B7A00, 0x2B7E30]:
    print("===", hex(start))
    for i in range(start, start+0x50, 4):
        w = struct.unpack_from("<I", d, i)[0]
        print("  ", hex(i), hex(w), w)
