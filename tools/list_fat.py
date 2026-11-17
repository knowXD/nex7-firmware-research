import sys
sys.path.append("nex7/pylibs")
from pyfatfs.PyFatFS import PyFatFS
fs = PyFatFS("nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked", read_only=True)
for f in fs.listdir("/"):
    try:
        st = fs.stat("/" + f)
        print(f, st.st_size)
    except Exception as e:
        print(f, "err", e)
fs.close()
