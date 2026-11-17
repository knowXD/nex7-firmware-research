import os, re
base = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked"
hits = []
for root, dirs, files in os.walk(base):
    for fn in files:
        p = os.path.join(root, fn)
        try:
            if os.path.getsize(p) > 40_000_000: continue
            d = open(p, "rb").read()
        except Exception:
            continue
        for kw in (b"scenario_run", b"scenario/", b"AVBB_SCN"):
            if kw in d:
                hits.append((os.path.relpath(p, base), kw.decode(), d.count(kw)))
for h in hits:
    print("%-45s %-14s x%d" % h)
