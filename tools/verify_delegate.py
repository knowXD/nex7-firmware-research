import sys, io, tarfile, struct
sys.path.append("nex7/pylibs"); sys.path.append("nex7/fwtool.py-master")
from fwtool.archive import lzpt
from fwtool.sony import dat, fdat

t = tarfile.open("nex7/new_delegate.tar")
m = t.extractfile(t.getmember("0700_part_image/dev/nflasha8")).read()
uf = next(lzpt.readLzpt(io.BytesIO(m)))
data = uf.contents.read()
ref = open("nex7/work_n8_delegate.img","rb").read()
print("nflasha8 match", data == ref, len(data))
print("stub magic", data[0xD1C400:0xD1C404].hex())

f = open("nex7/out_delegate/firmware_packed.dat","rb")
d = dat.readDat(f)
f.seek(d.firmwareData.offset)
dec = fdat._crypters["CXD4132"]().decrypt(io.BytesIO(f.read(0x4000))).read(64)
print("mode", dec[16:17], "ver", dec[12:16], "vmaj/min", dec[33], dec[32], "model", hex(struct.unpack_from("<I", dec, 36)[0]))
