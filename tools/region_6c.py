import struct
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p,"rb").read()
for start, end in [(0x6CB00, 0x6CC00), (0x6CFC0, 0x6D240)]:
    print("===", hex(start), "-", hex(end))
    for i in range(start, end, 4):
        w = struct.unpack_from("<I", d, i)[0]
        s = ""
        if 0xC3421000 <= w <= 0xC3C00000:
            off = w - 0xC3421000
            if off < len(d):
                seg = d[off:off+24]
                if all(32 <= c < 127 or c == 0 for c in seg[:8]):
                    s = seg.split(b"\x00")[0].decode("latin1")
        print("  ", hex(i), hex(w), s)
