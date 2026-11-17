import re
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/lib/libsencore.so"
d = open(p,"rb").read()
for m in re.finditer(rb"[\x20-\x7e]{4,}", d):
    s = m.group().decode("latin1")
    if any(k in s.lower() for k in ["plugin", ".so", "/usr", "/setting", "senser", "scenario"]):
        print(hex(m.start()), s[:110])
