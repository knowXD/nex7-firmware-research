import struct
SRC = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked"
DST = "nex7/work_nflasha8_bitrate.img"
d = bytearray(open(SRC,"rb").read())
off = 0x2548590
old = struct.unpack_from("<III", d, off)
print("old trio", old)
new = (46000000, 46000000, 30000000)
struct.pack_into("<III", d, off, *new)
open(DST,"wb").write(d)
chk = open(DST,"rb").read(off+12)
print("new trio", struct.unpack_from("<III", chk, off))
