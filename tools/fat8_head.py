d = open("nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked","rb").read()
print("size", len(d))
print("head", d[:64].hex())
print("mbr sig", d[510:512].hex())
# find FAT signatures
for sig in [b"FAT16", b"FAT32", b"FAT12"]:
    i = d.find(sig)
    print(sig, hex(i) if i>=0 else None)
# check ext2 magic 0x53EF at offset 1080 (superblock+56)
for off in [1024, 1024+1024, 0]:
    import struct
    if len(d) > off+1082:
        print("ext2 magic at", hex(off), hex(struct.unpack_from("<H", d, off+1080)[0]) if off else "")
