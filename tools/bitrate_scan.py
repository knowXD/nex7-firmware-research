import os, re, struct
BASE8 = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked"
AVCAM = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"

TARGETS = {28000000: "28M", 24000000: "24M", 18000000: "18M", 50000000: "50M", 46000000: "46M"}

def scan(path):
    d = open(path, "rb").read()
    hits = []
    for val, name in TARGETS.items():
        pat = struct.pack("<I", val)
        start = 0
        while True:
            i = d.find(pat, start)
            if i < 0: break
            hits.append((name, i))
            start = i + 1
    return hits, len(d)

print("### av-cam.bin ###")
h, n = scan(AVCAM)
print("size", n, "hits", len(h))
for nm, off in h[:20]:
    print("   0x%06X %s" % (off, nm))

print("\n### nflasha8 树 ###")
total = 0
for root, dirs, files in os.walk(BASE8):
    for fn in files:
        p = os.path.join(root, fn)
        try:
            if os.path.getsize(p) > 60_000_000: continue
        except Exception: continue
        h, n = scan(p)
        if h:
            total += len(h)
            rel = os.path.relpath(p, BASE8)
            print("   %-58s %s" % (rel, ", ".join("%s@0x%X" % (nm, off) for nm, off in h[:8])))
print("nflasha8 hits total:", total)
