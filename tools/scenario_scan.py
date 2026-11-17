import os, re
root = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked"
# list startbinary
for d in ["share/startbinary", "share/aveffect", "share/grm", "share/pmbp"]:
    p = os.path.join(root, d)
    if os.path.isdir(p):
        print("==", d, os.listdir(p)[:30])
# strings from scenario.elf
p = os.path.join(root, "bin/scenario.elf")
d = open(p,"rb").read()
print("== scenario.elf size", len(d))
for m in re.finditer(rb"[\x20-\x7e]{4,}", d):
    print("  ", hex(m.start()), m.group().decode("latin1")[:100])
