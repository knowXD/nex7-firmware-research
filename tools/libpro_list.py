import os, re
root = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked"
for dp, dn, fn in os.walk(root):
    for f in fn:
        if f.startswith("libpro") or f.startswith("libSnr"):
            print(os.path.relpath(os.path.join(dp,f), root), os.path.getsize(os.path.join(dp,f)))
