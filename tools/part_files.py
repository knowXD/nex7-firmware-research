import os, struct
base = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev"
for fn in os.listdir(base):
    print(fn, os.path.getsize(os.path.join(base, fn)))
