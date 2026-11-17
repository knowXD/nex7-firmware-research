import struct
for p, off in [("nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/lib/viewUnified4.so", 0x1F560),
               ("nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/lib/libObj.so", 0x57CF00)]:
    d = open(p,"rb").read()
    print("==", p.split("/")[-1], hex(off))
    for i in range(off-32, off+64, 4):
        w = struct.unpack_from("<I", d, i)[0]
        print("  ", hex(i), hex(w), w)
