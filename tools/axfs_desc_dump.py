d = open("nex7/work_initrd.img","rb").read()
for name, off in [("node_type",0x184), ("inode_file_size",0x25C), ("inode_name_offset",0x280), ("modes",0x310)]:
    b = d[off:off+40]
    print(name, "at", hex(off), b.hex())
    print("   bytes32-39:", b[32:40].hex())
