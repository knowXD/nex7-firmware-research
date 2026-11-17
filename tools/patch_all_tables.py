import sys, shutil
sys.path.append("nex7/pylibs")
from pyfatfs.PyFatFS import PyFatFS
SRC = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked"
DST = "nex7/work_fat_jpeg_all.img"
SCALE = 0.75
OFFSETS = [0x461092, 0x500464, 0x5097F4, 0x50FC60, 0x536E24, 0x555D64]
shutil.copyfile(SRC, DST)
fs = PyFatFS(DST, read_only=False)
with fs.openbin("/av-cam.bin", "r+b") as f:
    for off in OFFSETS:
        f.seek(off)
        tab = f.read(128)
        new = bytes(max(1, min(255, int(round(b * SCALE)))) for b in tab)
        f.seek(off)
        f.write(new)
        print(hex(off), list(tab[:8]), "->", list(new[:8]))
fs.close()
print("patched", DST)
