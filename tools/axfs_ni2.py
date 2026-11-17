d = open("nex7/work_initrd.img","rb").read()
for i in range(0x7EC, 0x8EC, 16):
    chunk = d[i:i+16]
    print("%04x" % i, " ".join("%02x" % b for b in chunk), "".join(chr(b) if 32<=b<127 else "." for b in chunk))
