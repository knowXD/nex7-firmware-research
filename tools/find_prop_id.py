import os, struct
pat = struct.pack("<I", 0x01070148)
roots = ["nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked",
         "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked"]
for root in roots:
    for dp, dn, fn in os.walk(root):
        for f in fn:
            p = os.path.join(dp, f)
            try: d = open(p,"rb").read()
            except: continue
            if pat in d:
                print(p.replace(root,""), hex(d.find(pat)), d.count(pat))
