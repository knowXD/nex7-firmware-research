import re
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/lib/libtestcmd_scn.so"
d = open(p,"rb").read()
print("size", len(d))
for m in re.finditer(rb"[ -~]{3,}", d):
    print(hex(m.start()), m.group()[:80].decode("latin1"))
