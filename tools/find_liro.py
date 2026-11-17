import os
roots = ["nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked",
         "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked"]
for root in roots:
    for dp, dn, fn in os.walk(root):
        for f in fn:
            p = os.path.join(dp, f)
            try:
                d = open(p, "rb").read()
            except Exception:
                continue
            if b"liro" in d.lower():
                print(p.replace(root, ""), len(d), d.lower().count(b"liro"))
