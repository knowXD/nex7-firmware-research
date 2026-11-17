d = open("nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/lib/libsencore.so","rb").read()
for off, n in [(0x18C40, 0x60), (0xD7F0, 0x40), (0x318A0, 0x60)]:
    print("==", hex(off))
    chunk = d[off:off+n]
    print(chunk.hex())
    print("".join(chr(b) if 32<=b<127 else "." for b in chunk))
