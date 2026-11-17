import sys, os
sys.path.append("nex7/pylibs"); sys.path.append("nex7/fwtool.py-master")
from fwtool.sony import dat
p = "nex7/a77/Update_SLTA77V107.exe"
d = open(p, "rb").read()
magic = bytes.fromhex("895546550d0a1a0a")
i = d.find(magic)
j = d.find(b"DEND", i)
print("size", len(d), "magic", hex(i), "DEND", hex(j))
if i >= 0 and j >= 0:
    blob = d[i:j+4]
    open("nex7/a77/firmware.dat", "wb").write(blob)
    print("carved", len(blob))
    dat.readDat(open("nex7/a77/firmware.dat", "rb"))
    print("readDat OK")
