import sys, shutil, struct
sys.path.append("nex7/pylibs")
from pyfatfs.PyFatFS import PyFatFS
SRC = "nex7/work_fat_qscale.img"
DST = "nex7/work_fat_qscale_bitrate.img"
shutil.copyfile(SRC, DST)
fs = PyFatFS(DST, read_only=False)
with fs.openbin("/av-cam.bin", "r+b") as f:
    f.seek(0x2B7A18)
    old = f.read(4)
    print("old", old.hex(), hex(struct.unpack("<I", old)[0]))
    new = struct.pack("<I", 0x02BDE780)
    f.seek(0x2B7A18)
    f.write(new)
    f.seek(0x2B7A18)
    print("new", f.read(4).hex())
fs.close()
print("patched", DST)
