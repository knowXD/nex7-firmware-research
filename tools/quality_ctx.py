import re
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/lib/libObj.so"
d = open(p,"rb").read()
for off in [0x44CBA5, 0x18A5ED]:
    seg = d[off-256:off+512]
    print("==", hex(off))
    for m in re.finditer(rb"[\x20-\x7e]{3,}", seg):
        print("  ", hex(off-256+m.start()), m.group().decode("latin1")[:100])
