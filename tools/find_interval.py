import os, re
base = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked"
kws = [b"INTERVAL", b"Interval", b"interval", b"INTVL", b"SELF_TIMER", b"SELFTIMER"]
for root, dirs, files in os.walk(base):
    for fn in files:
        p = os.path.join(root, fn)
        try:
            if os.path.getsize(p) > 30_000_000: continue
            d = open(p, "rb").read()
        except Exception: continue
        found = {k: d.count(k) for k in kws if k in d}
        if found:
            print("%-40s %s" % (os.path.relpath(p, base), {k.decode(): v for k, v in found.items()}))
