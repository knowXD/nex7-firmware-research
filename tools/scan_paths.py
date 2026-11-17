import os, re
root = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked"
pat_path = re.compile(rb"/(?:setting|usr|tmp|var|system|proc|mnt)[A-Za-z0-9_./-]{2,60}")
pat_kw = re.compile(rb"(dlopen|dlsym|LD_PRELOAD|/proc/klog|plugin|Plugin|extension|Extension|addon|AddOn)")
hits = {}
for dp, dn, fn in os.walk(root):
    for f in fn:
        p = os.path.join(dp, f)
        try: d = open(p,"rb").read()
        except: continue
        if len(d) > 30_000_000: continue
        rel = os.path.relpath(p, root)
        found = set()
        for m in pat_path.finditer(d):
            s = m.group().decode("latin1")
            found.add(("path", s))
        for m in pat_kw.finditer(d):
            found.add(("kw", m.group().decode("latin1")))
        if found:
            hits[rel] = found
# print interesting ones
for rel in sorted(hits):
    interesting = [s for t,s in hits[rel] if t=="kw" or s.startswith("/setting") or "klog" in s]
    if interesting:
        print("==", rel)
        for s in sorted(set(interesting))[:12]:
            print("   ", s)
