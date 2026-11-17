import re
a = open("nex7/fw101/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/vmlinux.bin","rb").read()
b = open("nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/vmlinux.bin","rb").read()
regions = [(0x1174f,0x11755),(0x117c3,0x117c9),(0x1183f,0x11845),(0x1456f5,0x1456f6),(0x145743,0x14575e),(0x145781,0x145782),(0x1ba6f1,0x1ba70c)]
for s,e in regions:
    print(hex(s), "old", a[s-16:e+16].decode("latin1","replace"))
    print("      new", b[s-16:e+16].decode("latin1","replace"))
# TPZL string context
i = a.find(b"TPZL")
print("TPZL ctx:", a[i-120:i+120].decode("latin1","replace"))
# cmpr string context
j = a.find(b"cmpr")
print("cmpr ctx:", a[j-120:j+160].decode("latin1","replace"))
