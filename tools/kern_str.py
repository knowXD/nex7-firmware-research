import re, os
base = "nex7/fw101/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/vmlinux.bin"
d = open(base,"rb").read()
def strings(b, minlen=4):
    return re.findall(rb"[\x20-\x7e]{%d,}" % minlen, b)
ss = [s.decode("latin1") for s in strings(d)]
keys = ["Linux version","2.6.29","alp","rt24","lz77","LZ77","cramfs","squashfs","jffs","init=","console=","CXD","cxd","sony","Sony","nflasha","MTD"]
for k in keys:
    hits = [s for s in ss if k in s]
    print("==", k, len(hits))
    for s in hits[:4]: print("   ", s[:120])
