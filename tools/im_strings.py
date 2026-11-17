import re
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/bin/im.elf"
d = open(p,"rb").read()
for m in re.finditer(rb"[\x20-\x7e]{6,}", d):
    s = m.group().decode("latin1")
    if any(k in s for k in ["BKID","liro","LIRO","RAM_ADDR","av-cam","load=","adr=","IMc"]):
        print(hex(m.start()), s[:120])
