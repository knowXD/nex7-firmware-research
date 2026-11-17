import sys, shutil, struct
sys.path.append("nex7/pylibs")
from pyfatfs.PyFatFS import PyFatFS
SRC = "nex7/work_fat_qscale.img"
DST = "nex7/work_fat_avcbits.img"
shutil.copyfile(SRC, DST)
fs = PyFatFS(DST, read_only=False)
OFFS = [(0xF97E0, "24M#1"), (0x35B730, "24M#2"), (0xF93BC, "18M#1"), (0xFA57C, "18M#2")]
with fs.openbin("/av-cam.bin", "r+b") as f:
    for off, name in OFFS:
        f.seek(off)
        old = struct.unpack("<I", f.read(4))[0]
        f.seek(off)
        f.write(struct.pack("<I", 46000000))
        print(name, hex(off), hex(old), "->", hex(46000000))
fs.close()
print("patched", DST)
