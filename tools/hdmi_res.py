import os, re
root = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked"
for dp, dn, fn in os.walk(root):
    for f in fn:
        p = os.path.join(dp, f)
        try: d = open(p,"rb").read()
        except: continue
        for kw in [b"1080p", b"1080i", b"HDMI Resolution", b"HDMI Resolution"]:
            if kw in d:
                i = d.find(kw)
                print(p.replace(root,""), kw.decode(), hex(i))
                break
