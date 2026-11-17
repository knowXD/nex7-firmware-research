import re
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p,"rb").read()
print("size", len(d))
print("head:", d[:64].hex(" "))
print("as ascii:", "".join(chr(c) if 32 <= c < 127 else "." for c in d[:64]))
for k in [b"ITRON", b"itron", b"T-Kernel", b"TKNL", b"TOPPERS", b"av-cam", b"AVCAM", b"version", b"Version"]:
    i = d.find(k)
    print(k, i)
