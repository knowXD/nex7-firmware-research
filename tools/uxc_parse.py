import struct
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/share/app/master_rec.uxc"
d = open(p,"rb").read()
print("size", len(d))
# u16 table from 0x10
vals = struct.unpack_from("<%dH" % ((len(d)-0x10)//2), d, 0x10)
print("first 40 u16:", [hex(v) for v in vals[:40]])
# count non-ffff
nz = [v for v in vals if v != 0xffff]
print("non-ffff count", len(nz), "max", hex(max(nz)) if nz else None)
# check whether values are ascending (offsets)
asc = all(nz[i] <= nz[i+1] for i in range(len(nz)-1))
print("ascending", asc)
# dump first page record at offset of largest? show record at 0x94
for off in [0x94, 0x1a9]:
    print("record at", hex(off), d[off:off+48].hex())
