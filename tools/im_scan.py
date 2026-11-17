import re
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/bin/im.elf"
d = open(p,"rb").read()
print("size", len(d))
for m in re.finditer(rb"[\x20-\x7e]{4,}", d):
    s = m.group().decode("latin1")
    if any(k in s for k in ["lib", ".so", "Obj", "LIRO", "av-cam", "exec", "/usr", "/setting", ".bin"]):
        print(hex(m.start()), s[:110])
