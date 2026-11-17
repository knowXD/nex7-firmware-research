import struct, re
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p,"rb").read()
for name, val in [("28M",28000000),("24M",24000000),("17M",17000000),("18M",18000000),("26M",26000000)]:
    pat = struct.pack("<I", val)
    hits = []
    i = d.find(pat)
    while i >= 0 and len(hits) < 8:
        hits.append(i); i = d.find(pat, i+1)
    print(name, val, "hits", [hex(h) for h in hits])
print("--- strings ---")
for m in re.finditer(rb"[\x20-\x7e]{6,}", d):
    s = m.group().decode("latin1")
    if any(k in s for k in ["ExCodecEncAvc", "hdAvcIfo", "AvcEnc", "RecodingRate", "RecordingRate", "Mbps"]):
        print(hex(m.start()), s[:100])
