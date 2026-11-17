import os, struct
base = "nex7/unpacked/firmware.tar_unpacked"
count = 0
for dp, dn, fn in os.walk(base):
    for f in fn:
        p = os.path.join(dp, f)
        if os.path.getsize(p) > 2_000_000 or os.path.getsize(p) < 16:
            continue
        d = open(p, "rb").read()
        hits = []
        for i in range(0, len(d)-4, 4):
            w = struct.unpack_from("<I", d, i)[0]
            if 0xC3000000 <= w <= 0xC3FFFFFF:
                hits.append((i, w))
        if hits and len(hits) < 200:
            print(p.replace(base, ""), "hits", len(hits), [(hex(o), hex(w)) for o, w in hits[:5]])
            count += 1
print("files with hits:", count)
