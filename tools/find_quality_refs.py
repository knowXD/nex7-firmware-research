import os
root = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked"
for dp, dn, fn in os.walk(root):
    for f in fn:
        p = os.path.join(dp, f)
        try: d = open(p,"rb").read()
        except: continue
        if b"JPG_QUALITY" in d or b"PARAMID_DATA_JPEG_QUALITY" in d:
            print(p.replace(root,""), len(d), "JPG_QUALITY", d.count(b"JPG_QUALITY"), "PARAMID", d.count(b"PARAMID_DATA_JPEG_QUALITY"))
