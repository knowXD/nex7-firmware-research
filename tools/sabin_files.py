import sys, struct, re
sys.path.append("nex7/pylibs")
from pyfatfs.PyFatFS import PyFatFS
fs = PyFatFS("nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked", read_only=True)
for n in fs.listdir("/sabin"):
    with fs.openbin("/sabin/" + n) as f:
        d = f.read()
    print("==", n, len(d), d[:8].hex())
    for name, val in [("28M",28000000),("24M",24000000),("18M",18000000),("17M",17000000)]:
        pat = struct.pack("<I", val)
        hits = []
        i = d.find(pat)
        while i >= 0 and len(hits) < 4:
            hits.append(i); i = d.find(pat, i+1)
        if hits: print("   ", name, [hex(h) for h in hits])
    strs = [m.group().decode("latin1") for m in re.finditer(rb"[\x20-\x7e]{8,}", d) if b"Avc" in m.group() or b"AVC" in m.group() or b"rate" in m.group().lower()]
    for s in strs[:5]:
        print("    str", s[:80])
fs.close()
