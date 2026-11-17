import re
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p, "rb").read()
src = []
for m in re.finditer(rb"[A-Za-z0-9_./\\-]+\.(?:cpp|cxx|cc|c|hpp|h)\x00", d):
    s = m.group()[:-1].decode("latin1")
    src.append((m.start(), s))
print("source refs", len(src))
seen = set()
for off, s in src:
    if s in seen: continue
    seen.add(s)
print("unique", len(seen))
for off, s in src[:120]:
    print(hex(off), s)
