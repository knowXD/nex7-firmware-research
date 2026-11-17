import re, struct
d = open("nex7/work_initrd.img","rb").read()
print("size", len(d))
print("header:", d[:64].hex())
# look for strings
hits = {}
for kw in [b"/init", b"busybox", b"mount", b"S00", b"rcS", b"linuxrc", b"ash"]:
    i = d.find(kw)
    hits[kw] = i
print(hits)
# sample first 30 readable strings >= 6 chars
cnt = 0
for m in re.finditer(rb"[\x20-\x7e]{6,}", d):
    print(hex(m.start()), m.group().decode("latin1")[:80])
    cnt += 1
    if cnt >= 30: break
