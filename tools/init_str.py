import re
d = open("nex7/initrd_unpacked/sbin/init","rb").read()
print("size", len(d), "magic", d[:4].hex())
for m in re.finditer(rb"[\x20-\x7e]{5,}", d):
    print(hex(m.start()), m.group().decode("latin1")[:110])
