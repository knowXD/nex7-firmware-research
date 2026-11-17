import re
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/initrd.img_unpacked/kmod/liro.ko"
d = open(p, "rb").read()
print("size", len(d), "magic", d[:4])
for m in re.finditer(rb"[\x20-\x7e]{5,}", d):
    s = m.group().decode("latin1")
    if any(k in s.lower() for k in ["liro","addr","bkid","ram","boot","cpu","core","mail","msg","irq"]):
        print(hex(m.start()), s[:120])
