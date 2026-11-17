import struct
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p,"rb").read()
base = 0xC3420000
for off in [0x1080, 0x1168, 0x10d0]:
    needle = struct.pack("<I", base + off)
    hits = []
    i = d.find(needle)
    while i >= 0 and len(hits) < 10:
        hits.append(i); i = d.find(needle, i+1)
    print(hex(base+off), "refs at", [hex(h) for h in hits])
# look for pointer table around the first hits
