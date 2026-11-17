import re
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/bin/sen.elf"
d = open(p,"rb").read()
for m in re.finditer(rb"[\x20-\x7e]{4,}", d):
    print(hex(m.start()), m.group().decode("latin1")[:110])
