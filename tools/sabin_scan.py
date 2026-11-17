import sys, struct
sys.path.append("nex7/pylibs")
from pyfatfs.PyFatFS import PyFatFS
fs = PyFatFS("nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked", read_only=True)
with fs.openbin("/sabin") as f:
    d = f.read()
fs.close()
print("sabin size", len(d), "magic", d[:16].hex())
for name, val in [("28M",28000000),("24M",24000000),("18M",18000000),("17M",17000000),("26M",26000000),("16M",16000000),("12M",12000000)]:
    pat = struct.pack("<I", val)
    hits = []
    i = d.find(pat)
    while i >= 0 and len(hits) < 6:
        hits.append(i); i = d.find(pat, i+1)
    print(name, "hits", [hex(h) for h in hits])
