import struct
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p,"rb").read()
base = 0xC3421000
for start in [0x3A0F80, 0x3A1030]:
    print("===", hex(start))
    for i in range(start, start+0x60, 4):
        w = struct.unpack_from("<I", d, i)[0]
        s = ""
        if base <= w <= base+len(d):
            off = w-base
            seg = d[off:off+32]
            if all(32 <= c < 127 or c==0 for c in seg[:8]):
                s = seg.split(b"\x00")[0].decode("latin1")
            else:
                s = "code?"
        print("  ", hex(i), hex(w), s)
