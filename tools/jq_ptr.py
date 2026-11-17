import struct
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p,"rb").read()
for base in [0xC3000000,0xC3200000,0xC3400000,0xC3420000,0xC3500000,0xC3600000]:
    for off in [0x461092,0x46114f]:
        w = base + off
        needle = struct.pack("<I", w)
        hits = []
        i = d.find(needle)
        while i >= 0 and len(hits) < 4:
            hits.append(hex(i)); i = d.find(needle, i+1)
        if hits:
            print(hex(w), "refs", hits)
