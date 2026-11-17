p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p,"rb").read()
for s in [b"dgi_jpeg_qtable_calc_qscale", b"Invalid Jpeg Quality", b"encodeQuality"]:
    i = d.find(s)
    print(s, hex(i) if i>=0 else None, d.count(s))
