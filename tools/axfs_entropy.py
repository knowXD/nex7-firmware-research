from collections import Counter
d = open("nex7/work_initrd.img","rb").read()
for name, off, size in [("node_type",0x37C,1136), ("inode_file_size",0x34F8,2068), ("modes",0x5D5C,104)]:
    blob = d[off:off+size]
    c = Counter(blob)
    print(name, "distinct", len(c), "top", c.most_common(6))
    print("  first 24", blob[:24].hex())
