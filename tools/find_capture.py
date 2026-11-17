import os, re
base = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked"
kws = [b"STILL", b"SHUTTER", b"CAPTURE", b"STILL_ENC", b"scn_", b"SCN_"]
hits = {}
for root, dirs, files in os.walk(base):
    for fn in files:
        if not fn.endswith(".so") and not fn.endswith(".elf"): continue
        p = os.path.join(root, fn)
        try:
            if os.path.getsize(p) > 30_000_000: continue
            d = open(p, "rb").read()
        except Exception: continue
        for k in (b"STILL", b"SHUTTER", b"CAPTURE"):
            for m in re.finditer(k, d):
                s = d[max(0,m.start()-30): m.start()+40]
                txt = "".join(chr(b) if 32 <= b < 127 else "." for b in s)
                hits.setdefault(k.decode(), set()).add((fn, txt[:60]))
print("== 含 STILL/SHUTTER/CAPTURE 的位置（前几例）==")
for k, v in hits.items():
    print("\n[%s] %d 例" % (k, len(v)))
    for fn, txt in list(v)[:6]:
        print("   %-32s %s" % (fn, txt))
