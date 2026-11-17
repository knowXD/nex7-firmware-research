import sys, shutil
sys.path.append("nex7/pylibs")
from pyfatfs.PyFatFS import PyFatFS

SRC = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked"
SCALE = float(sys.argv[1]) if len(sys.argv) > 1 else 0.75
DST = sys.argv[2] if len(sys.argv) > 2 else "nex7/work_fat_jpeg.img"
shutil.copyfile(SRC, DST)
fs = PyFatFS(DST, read_only=False)
with fs.openbin("/av-cam.bin", "r+b") as f:
    f.seek(0x461092)
    tab = f.read(128)
    new = bytes(max(1, min(255, int(round(b * SCALE)))) for b in tab)
    f.seek(0x461092)
    f.write(new)
fs.close()
print("scale", SCALE, "first", list(new[:8]))
