import re
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/share/app/string_english.uxc"
d = open(p,"rb").read()
print("size", len(d))
i = d.find(b"NTSC")
for off in [i]:
    seg = d[max(0,off-400):off+400]
    for m in re.finditer(rb"[\x20-\x7e]{3,}", seg):
        print(hex(off-400+m.start()), m.group().decode("latin1")[:100])
