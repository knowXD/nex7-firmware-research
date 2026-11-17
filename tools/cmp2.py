import os, sys, tarfile, hashlib, io
sys.path.append("nex7/pylibs"); sys.path.append("nex7/fwtool.py-master")
from fwtool.lz77 import inflateLz77

def tpzl_struct(p):
    import struct
    d = open(p,"rb").read()
    magic, bs, tocoff, tocsz = struct.unpack_from("<4sIII", d, 0)
    n = tocsz//8
    pat = {}
    for i in range(n):
        off, size = struct.unpack_from("<II", d, tocoff+i*8)
        b = io.BytesIO(d[off:off+size]); read=0; chunks=[]
        while read < (1<<bs):
            c = len(inflateLz77(b)); chunks.append(c); read += c
            if len(chunks)>64: break
        key = tuple(chunks[:3]) if len(chunks)>3 else tuple(chunks)
        pat[key] = pat.get(key,0)+1
    return len(d), bs, n, pat

for ver, base in [("1.02","nex7/fw102"),("1.03","nex7")]:
    u = os.path.join(base,"unpacked")
    parts = os.path.join(u,"firmware.tar_unpacked/0700_part_image/dev")
    print("==", ver)
    for f in ["nflasha3","nflasha8"]:
        p = os.path.join(parts,f)
        if os.path.exists(p):
            sz,bs,n,pat = tpzl_struct(p)
            print("  ",f,"img",sz,"blockSize",bs,"blocks",n,"patterns",list(pat.items())[:4])
    av = os.path.join(u,"firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin")
    if os.path.exists(av):
        d = open(av,"rb").read()
        print("   av-cam", len(d), hashlib.sha256(d).hexdigest()[:20])
    av8 = os.path.join(u,"firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked")
    print("   nflasha8_unpacked exists", os.path.isdir(av8))
