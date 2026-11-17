import re
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/lib/libObj.so"
d = open(p,"rb").read()
i = d.find(b"NTSC")
print("libObj NTSC at", hex(i))
seg = d[max(0,i-300):i+300]
for m in re.finditer(rb"[\x20-\x7e]{4,}", seg):
    print(hex(i-300+m.start()), m.group().decode("latin1")[:100])
p2 = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/share/app/string_english.uxc"
d2 = open(p2,"rb").read()
for m in re.finditer(rb"[\x20-\x7e]{6,}", d2):
    s = m.group().decode("latin1")
    if "Selector" in s or "NTSC" in s or "PAL" in s:
        print("uxc", hex(m.start()), s[:100])
