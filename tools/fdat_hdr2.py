import sys, io, struct
sys.path.append("nex7/pylibs"); sys.path.append("nex7/fwtool.py-master")
from fwtool.sony import dat, fdat

for name, p in [("out_stock","nex7/out_stock/firmware_packed.dat"),
                ("out_stock99","nex7/out_stock99/firmware_packed.dat"),
                ("out_jpeg_v2","nex7/out_jpeg_v2/firmware_packed.dat")]:
    f = open(p, "rb")
    d = dat.readDat(f)
    part = d.firmwareData
    print(name, "part", type(part).__name__, getattr(part, "offset", None), getattr(part, "size", None))
    f.seek(part.offset if hasattr(part, "offset") else 0)
    blob = f.read(0x4000)
    crypter = fdat._crypters["CXD4132"]()
    dec = crypter.decrypt(io.BytesIO(blob)).read(256)
    magic = dec[0:8]
    ver = dec[12:16]
    mode = dec[16:17]
    vmin, vmaj = dec[32], dec[33]
    model, region = struct.unpack_from("<II", dec, 36)
    print("   magic", magic, "mode", mode, "ver", ver, "vmaj/min", vmaj, vmin, "model", hex(model), "region", hex(region))
