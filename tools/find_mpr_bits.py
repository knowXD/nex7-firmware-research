import struct
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/lib/libmpr.so"
d = open(p,"rb").read()
for name, val in [("28M",28000000),("24M",24000000),("17M",17000000),("9M",9000000),("16M",16000000),("12M",12000000)]:
    pat = struct.pack("<I", val)
    hits = []
    i = d.find(pat)
    while i >= 0 and len(hits) < 8:
        hits.append(i); i = d.find(pat, i+1)
    print(name, val, "hits", [hex(h) for h in hits])
