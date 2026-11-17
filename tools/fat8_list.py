import sys
sys.path.append("nex7/pylibs")
from pyfatfs.PyFatFS import PyFatFS
fs = PyFatFS("nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked", read_only=True)
for name in fs.listdir("/"):
    try:
        info = fs.getinfo("/" + name)
        print(name, "dir" if info.is_dir else "file", info.size)
    except Exception as e:
        print(name, "err", e)
fs.close()
