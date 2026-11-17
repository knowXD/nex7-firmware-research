import os
root = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/lib"
for f in sorted(os.listdir(root)):
    print(f, os.path.getsize(os.path.join(root,f)))
