import os, tarfile, hashlib
def members(p):
    tf = tarfile.open(p, "r:")
    return [(m.name, m.size) for m in tf.getmembers() if m.isfile()]
for ver, base in [("1.02","nex7/fw102/unpacked"),("1.03","nex7/unpacked")]:
    cfg = open(os.path.join(base,"config.yaml")).read()
    verline = [l for l in cfg.splitlines() if "version" in l.lower()]
    print(ver, "config:", verline[:3])
    ms = members(os.path.join(base,"firmware.tar"))
    print("  members:")
    for n,s in ms: print("   ", n, s)
    av = os.path.join(base,"firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
    if os.path.exists(av):
        d = open(av,"rb").read()
        print("  av-cam", len(d), hashlib.sha256(d).hexdigest()[:16])
