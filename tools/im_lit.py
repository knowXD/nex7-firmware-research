import struct
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/bin/im.elf"
d = open(p,"rb").read()
for tgt in [0x401c, 0x4070, 0x3fe4, 0x4050]:
    needle = struct.pack("<I", tgt)
    hits = []
    i = d.find(needle)
    while i >= 0 and len(hits) < 8:
        hits.append(hex(i)); i = d.find(needle, i+1)
    print(hex(tgt), hits)
