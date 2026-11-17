import re
p = "nex7/unpacked/updater.img_unpacked/bodylib/libupdaterbody.so"
d = open(p, "rb").read()
print("size", len(d), "magic", d[:4])
for m in re.finditer(rb"[\x20-\x7e]{5,}", d):
    s = m.group().decode("latin1")
    if any(k in s.lower() for k in ["version","guard","invalid","model","region","status","error","update","flash","write","verify"]):
        print(hex(m.start()), s[:120])
