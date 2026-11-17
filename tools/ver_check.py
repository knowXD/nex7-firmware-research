import sys
sys.path.append("nex7/pylibs"); sys.path.append("nex7/fwtool.py-master")
from fwtool.sony import dat, fdat
for name, p in [("out_stock","nex7/out_stock/firmware_packed.dat"), ("out_stock99","nex7/out_stock99/firmware_packed.dat")]:
    d = dat.readDat(open(p, "rb"))
    # FDAT header is at the start of firmwareData; read header without full decrypt
    f = fdat.readFdat(open(p, "rb")) if False else None
    print(name, "firmwareData", d.firmwareData.size if hasattr(d.firmwareData,'size') else '?')
