import struct
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p,"rb").read()
base = 0xC3421000
targets = {"setQComp":0x506308, "setQ":0x5062F0, "getEs":0x5062F2, "movieQ":0x506308}
for name, off in targets.items():
    w = base + off
    needle = struct.pack("<I", w)
    hits = []
    i = d.find(needle)
    while i >= 0 and len(hits) < 10:
        hits.append(i); i = d.find(needle, i+1)
    print(name, hex(w), [hex(h) for h in hits])
# strings near 0x5062xx
import re
seg = d[0x506280:0x506360]
for m in re.finditer(rb"[\x20-\x7e]{6,}", seg):
    print(hex(0x506280+m.start()), m.group().decode("latin1"))
