import os, sys, struct, io, hashlib
sys.path.append("nex7/pylibs"); sys.path.append("nex7/fwtool.py-master")
from fwtool.lz77 import inflateLz77

def tpzl(p):
    d = open(p,"rb").read()
    magic, bs, tocoff, tocsz = struct.unpack_from("<4sIII", d, 0)
    n = tocsz//8
    pats = {}
    for i in range(n):
        off, size = struct.unpack_from("<II", d, tocoff+i*8)
        b = io.BytesIO(d[off:off+size]); read=0; ch=[]
        while read < (1<<bs):
            c = len(inflateLz77(b)); ch.append(c); read += c
            if len(ch) > 64: break
        key = tuple(ch[:2])
        pats[key] = pats.get(key, 0) + 1
    return len(d), bs, n, pats

for ver, u in [("1.01","nex7/fw101/unpacked"),("1.02","nex7/fw102/unpacked"),("1.03","nex7/unpacked")]:
    cfg = open(os.path.join(u,"config.yaml")).read()
    vline = [l.strip() for l in cfg.splitlines() if "version" in l.lower()]
    print("==", ver, vline)
    parts = os.path.join(u,"firmware.tar_unpacked/0700_part_image/dev")
    for f in ["nflasha3","nflasha8"]:
        p = os.path.join(parts,f)
        if os.path.exists(p):
            sz,bs,n,pats = tpzl(p)
            print("  ", f, "img", sz, "bs", bs, "blocks", n, "patterns", dict(list(pats.items())[:3]))
    av = os.path.join(parts,"nflasha3_unpacked_unpacked/av-cam.bin")
    if os.path.exists(av):
        d = open(av,"rb").read()
        print("   av-cam", len(d), hashlib.sha256(d).hexdigest()[:20])
