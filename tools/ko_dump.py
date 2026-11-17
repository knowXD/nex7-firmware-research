p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/initrd.img_unpacked/kmod/liro.ko"
d = open(p,"rb").read()
for off in [0x34, 0x58, 0x570, 0xa20, 0x86fc]:
    print(hex(off), d[off:off+32].hex(" "))
