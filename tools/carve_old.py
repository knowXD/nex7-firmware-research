import sys, os
sys.path.append("nex7/pylibs"); sys.path.append("nex7/fwtool.py-master")
from fwtool.sony import dat
magic = bytes.fromhex("895546550d0a1a0a")
pairs = [("nex7/fw101/Sony_Update_NEX7V101/Sony_Update_NEX7V101.exe", "nex7/fw101/firmware.dat"),
         ("nex7/fw102/Sony_Update_NEX7_V102w/Sony_Update_NEX7_V102w.exe", "nex7/fw102/firmware.dat")]
for exe, out in pairs:
    d = open(exe, "rb").read()
    i = d.find(magic)
    j = d.find(b"DEND", i)
    print(os.path.basename(exe), "size", len(d), "magic", hex(i) if i >= 0 else None, "DEND", hex(j) if j >= 0 else None)
    if i >= 0 and j >= 0:
        blob = d[i:j+4]
        open(out, "wb").write(blob)
        print("  carved", len(blob))
        try:
            dat.readDat(open(out, "rb"))
            print("  readDat OK")
        except Exception as e:
            print("  readDat ERR", str(e)[:120])
