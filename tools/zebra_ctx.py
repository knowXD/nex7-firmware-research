import re
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/lib/libObj.so"
d = open(p,"rb").read()
for kw in [b"MSGID_SET_ZEBRA_CMD", b"ExecCommandSetZebra", b"SET_ZEBRA"]:
    i = d.find(kw)
    print(kw, hex(i) if i>=0 else None, d.count(kw))
    if i >= 0:
        seg = d[max(0,i-200):i+200]
        for m in re.finditer(rb"[\x20-\x7e]{6,}", seg):
            print("   ", hex(i-200+m.start()), m.group().decode("latin1")[:100])
