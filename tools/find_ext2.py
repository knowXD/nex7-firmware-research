import struct, re
d = open("nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked","rb").read()
hits = [m.start() for m in re.finditer(b"\xef\x53", d)]
for h in hits:
    sb = h - 56
    if sb < 0 or sb + 1024 > len(d): continue
    inodes = struct.unpack_from("<I", d, sb+0)[0]
    blocks = struct.unpack_from("<I", d, sb+4)[0]
    logbs = struct.unpack_from("<I", d, sb+24)[0]
    if 100 < inodes < 1000000 and 100 < blocks < 2000000 and logbs <= 4:
        print("candidate sb at", hex(sb), "inodes", inodes, "blocks", blocks, "logbs", logbs)
