import re, struct
d = open("nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/lib/libsencore.so","rb").read()
start, end = 0x31000, 0x36000
for m in re.finditer(rb"[A-Z][A-Z0-9_]{4,40}", d[start:end]):
    off = start + m.start()
    name = m.group().decode()
    prev = d[off-8:off]
    print(hex(off), name, prev.hex())
