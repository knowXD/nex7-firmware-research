import sys, struct
sys.path.append("nex7/pylibs")
from pyfatfs.PyFatFS import PyFatFS
fs = PyFatFS("nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked", read_only=True)
with fs.openbin("/initrd.img") as f:
    d = f.read()
fs.close()
print("size", len(d))
print("first 32:", d[:32].hex())
print("ascii:", d[:16])
# try known magics
magics = {b"\x1f\x8b\x08":"gzip", b"BZh":"bzip2", b"\xfd7zXZ":"xz", b"\x28\xb5\x2f\xfd":"zstd", b"070701":"cpio-newc", b"070702":"cpio-crc", b"\x89PNG":"png", b"hsqs":"squashfs", b"UBI#":"ubi", b"\x5d\x00\x00":"lzma?"}
for m, name in magics.items():
    if d.startswith(m):
        print("magic:", name)
open("nex7/work_initrd.img","wb").write(d)
print("saved")
