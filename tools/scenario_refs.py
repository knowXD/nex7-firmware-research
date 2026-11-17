import os, re
root = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked"
for dp, dn, fn in os.walk(root):
    for f in fn:
        p = os.path.join(dp, f)
        try: d = open(p,"rb").read()
        except: continue
        if b"/usr/scenario" in d or b"scenario/" in d or b"SCN_" in d:
            print("==", os.path.relpath(p, root))
            for m in re.finditer(rb"[\x20-\x7e]{4,}", d):
                s = m.group().decode("latin1")
                if "scenario" in s.lower() or "SCN_" in s:
                    print("   ", s[:110])
