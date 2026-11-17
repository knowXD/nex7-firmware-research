import os, re
root = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked"
hits = []
for dp, dn, fn in os.walk(root):
    for f in fn:
        p = os.path.join(dp, f)
        try: d = open(p,"rb").read()
        except: continue
        for kw in [b"PAL/NTSC", b"NTSC", b"PAL"]:
            if kw in d:
                i = d.find(kw)
                hits.append((p.replace(root,""), kw.decode(), hex(i)))
                break
for h in hits[:20]:
    print(h)
print("total files", len(hits))
