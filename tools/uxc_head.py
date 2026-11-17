import struct
for name in ["TA_EmptyAnimation.uxc", "color_cmn.uxc", "master_menu.uxc", "master_rec.uxc"]:
    p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/share/app/" + name
    d = open(p,"rb").read()
    print("==", name, len(d))
    for i in range(0, min(96, len(d)), 16):
        chunk = d[i:i+16]
        print("  %04x" % i, " ".join("%02x" % b for b in chunk), "".join(chr(b) if 32<=b<127 else "." for b in chunk))
