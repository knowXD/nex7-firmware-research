import os, hashlib
bases = [("1.01","nex7/fw101/unpacked"),("1.02","nex7/fw102/unpacked"),("1.03","nex7/unpacked")]
for ver,u in bases:
    d = os.path.join(u,"firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked")
    for f in ["vmlinux.bin","initrd.img","av-cam.bin"]:
        p = os.path.join(d,f)
        if os.path.exists(p):
            b = open(p,"rb").read()
            print(ver, f, len(b), hashlib.sha256(b).hexdigest()[:16])
