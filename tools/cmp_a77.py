import os, hashlib
def show(ver, base):
    print("=====", ver, base)
    mc = os.path.join(base, "firmware.tar_unpacked/0100_config/mount.conf")
    if os.path.exists(mc):
        for line in open(mc):
            if line.startswith("/dev/"):
                print("  ", line.strip())
    d3 = os.path.join(base, "firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked")
    for f in ["vmlinux.bin","initrd.img","av-cam.bin"]:
        p = os.path.join(d3,f)
        if os.path.exists(p):
            b = open(p,"rb").read()
            print("  ", f, len(b), hashlib.sha256(b).hexdigest()[:12], b[:8].hex())
    d8 = os.path.join(base, "firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked")
    print("   nflasha8 exists:", os.path.isdir(d8))
    if os.path.isdir(d8):
        hits = []
        for dp, dn, fn in os.walk(d8):
            for f in fn:
                if f in ("s_start_android.sh","ramdisk.img","build.prop"):
                    hits.append(os.path.join(dp,f).replace(d8,""))
        print("   android files:", hits[:5])
show("NEX-7 1.03", "nex7/unpacked")
show("A77 1.07", "nex7/a77/unpacked")
