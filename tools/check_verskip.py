import sys, io, struct
sys.path.append("nex7/pylibs"); sys.path.append("nex7/fwtool.py-master")
from fwtool.sony import dat, fdat
p = "nex7/out_verskip/firmware_packed.dat"
f = open(p, "rb")
d = dat.readDat(f)
part = d.firmwareData
f.seek(part.offset)
blob = f.read(0x4000)
dec = fdat._crypters["CXD4132"]().decrypt(io.BytesIO(blob)).read(64)
print("magic", dec[0:8], "mode", dec[16:17], "ver", dec[12:16], "vmaj/min", dec[33], dec[32], "model", hex(struct.unpack_from("<I", dec, 36)[0]))
