import sys, shutil, struct
sys.path.append("nex7/pylibs")
from pyfatfs.PyFatFS import PyFatFS
SRC = "nex7/work_fat_qscale_bitrate.img"
DST = "nex7/work_fat_qscale_bitrate2.img"
shutil.copyfile(SRC, DST)
fs = PyFatFS(DST, read_only=False)
with fs.openbin("/av-cam.bin", "r+b") as f:
    for off, name in [(0x2B7A1C, "12M")]:
        f.seek(off)
        old = f.read(4)
        print(name, "old", old.hex(), hex(struct.unpack("<I", old)[0]))
        f.seek(off)
        f.write(struct.pack("<I", 0x02BDE780))
        f.seek(off)
        print(name, "new", f.read(4).hex())
fs.close()
print("patched", DST)
