import sys, shutil
sys.path.append("nex7/pylibs")
from pyfatfs.PyFatFS import PyFatFS
SRC = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked"
DST = "nex7/work_fat_qscale.img"
shutil.copyfile(SRC, DST)
fs = PyFatFS(DST, read_only=False)
with fs.openbin("/av-cam.bin", "r+b") as f:
    # 0x6D032: mov r7, r0 (07 46) -> lsrs r7, r0, #1 (47 08)
    f.seek(0x6D032)
    old = f.read(2)
    print("old bytes", old.hex())
    f.seek(0x6D032)
    f.write(bytes.fromhex("4708"))
    f.seek(0x6D032)
    print("new bytes", f.read(2).hex())
fs.close()
print("patched", DST)
