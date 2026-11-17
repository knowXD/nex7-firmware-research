d = open("nex7/work_initrd.img","rb").read()
for name, off in [("xip",0x6000), ("byte_aligned",0x1F6000), ("compressed",0x1FA7A2), ("strings",0x2F7751)]:
    print(name, hex(off), d[off:off+32].hex())
# entropy sample
from collections import Counter
for name, off, size in [("xip",0x6000,200000), ("compressed",0x1FA7A2,100000)]:
    blob = d[off:off+size]
    c = Counter(blob)
    print(name, "distinct", len(c), "zero%", 100*blob.count(0)/len(blob))
