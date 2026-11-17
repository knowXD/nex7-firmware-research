p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/vmlinux.bin"
d = open(p, "rb").read()
for kw in [b"TMP19A", b"tmp19a", b"Toshiba", b"TOSHIBA", b"tosh", b"ARM926", b"926", b"ARMv5", b"ARMv6", b"ARMv7"]:
    n = d.count(kw)
    i = d.find(kw)
    print("%-10s x%-4d %s" % (kw.decode(), n, ("0x%X" % i) if i >= 0 else "-"))
    if 0 <= i and n <= 8:
        s = d[max(0,i-70): i+90]
        print("      ", "".join(chr(b) if 32 <= b < 127 else "." for b in s))
