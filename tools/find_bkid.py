import os
base = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked"
for dp, dn, fn in os.walk(base):
    for f in fn:
        p = os.path.join(dp, f)
        if not f.endswith((".ko", ".elf", ".bin", ".so")):
            continue
        try:
            d = open(p, "rb").read()
        except Exception:
            continue
        if b"BKID_RAM_ADDR" in d or b"RAM_ADDR_GP_LIRO" in d:
            print(p.replace(base, ""), len(d))
