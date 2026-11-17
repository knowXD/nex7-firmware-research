import struct, re
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/lib/libmpr.so"
d = open(p,"rb").read()
for start in [0x4ED940, 0x6E9D00, 0x6EA040]:
    print("===", hex(start))
    for i in range(start, start+0xC0, 4):
        w = struct.unpack_from("<I", d, i)[0]
        s = ""
        if 0x1000 <= w < len(d):
            seg = d[w:w+32]
            if all(32 <= c < 127 or c == 0 for c in seg[:10]):
                s = seg.split(b"\x00")[0].decode("latin1")
        print("  ", hex(i), hex(w), w, s)
