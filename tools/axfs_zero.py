d = open("nex7/work_initrd.img","rb").read()
for name, off, size in [("inode_file_size",0x34F8,2068), ("inode_name_offset",0x3D0C,2068),
                        ("inode_num_entries",0x4520,2068), ("inode_mode_index",0x4D34,2068),
                        ("inode_array_index",0x5548,2068), ("node_index",0x7EC,4544)]:
    blob = d[off:off+size]
    z = blob.count(0)
    print(name, "zero%%=%.1f" % (100*z/len(blob)), "first16", blob[:16].hex())
