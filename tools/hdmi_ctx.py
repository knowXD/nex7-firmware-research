import re
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/share/app/string_english.uxc"
d = open(p,"rb").read()
i = d.find(b"1080p")
seg = d[max(0,i-600):i+600]
for m in re.finditer(rb"[\x20-\x7e]{4,}", seg):
    print(hex(i-600+m.start()), m.group().decode("latin1")[:120])
