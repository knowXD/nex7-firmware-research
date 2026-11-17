import os, re
root = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked"
# list top-level bins and libs
for d in ["bin", "sbin", "lib", "usr/bin", "usr/sbin", "usr/lib"]:
    p = os.path.join(root, d)
    if os.path.isdir(p):
        names = sorted(os.listdir(p))
        print("==", d, len(names))
        for n in names[:40]:
            fp = os.path.join(p, n)
            if os.path.isfile(fp):
                print("   ", n, os.path.getsize(fp))
