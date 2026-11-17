import re
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/vmlinux.bin"
d = open(p, "rb").read()
for kw in [b"CXD4132", b"MPCore", b"ARM11", b"arm11", b"CXD", b"Diadem", b"cxd"]:
    n = d.count(kw)
    i = d.find(kw)
    print("%-10s x%-4d %s" % (kw.decode(), n, ("0x%X" % i) if i >= 0 else "-"))
    if 0 <= i:
        s = d[max(0,i-60): i+80]
        print("      ", "".join(chr(b) if 32 <= b < 127 else "." for b in s))
