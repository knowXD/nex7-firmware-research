import re
paths = {
 "libObj": "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/lib/libObj.so",
 "libmpr": "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/lib/libmpr.so",
}
keys = [b"Zebra", b"ZEBRA", b"AntiFlicker", b"ANTIFLICKER", b"Anti-Flicker", b"HDMI", b"CleanHDMI", b"29:50", b"REC_LIMIT", b"RecLimit", b"MovieLimit"]
for name, p in paths.items():
    d = open(p,"rb").read()
    print("==", name, len(d))
    for k in keys:
        c = d.count(k)
        if c:
            i = d.find(k)
            print("   ", k, c, hex(i), d[max(0,i-40):i+60])
