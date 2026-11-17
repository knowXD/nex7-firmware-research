import os, re
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/lib/libbackup.so"
print("size", os.path.getsize(p))
d = open(p,"rb").read()
for kw in [b"Quality", b"quality", b"JPEG", b"Jpeg", b"PROP", b"prop"]:
    print(kw, d.count(kw), hex(d.find(kw)) if d.find(kw)>=0 else None)
# sample property-like strings
for m in re.finditer(rb"[A-Za-z_][A-Za-z0-9_]{6,}", d):
    s = m.group().decode("latin1")
    if "Qual" in s or "JPEG" in s or "Jpeg" in s:
        print(hex(m.start()), s[:80])
