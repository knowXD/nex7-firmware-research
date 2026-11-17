import re
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p,"rb").read()
for kw in [b"sabin", b"SABIN", b"Sabin"]:
    cnt = d.count(kw)
    print(kw, cnt)
    i = d.find(kw)
    if i >= 0: print("  at", hex(i), d[i-32:i+48])
# also search FAT image for sabin file entry
p2 = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked"
d2 = open(p2,"rb").read()
for kw in [b"SABIN", b"sabin"]:
    cnt = d2.count(kw)
    print("fat", kw, cnt)
