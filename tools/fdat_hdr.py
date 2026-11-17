import struct
for name, p in [("out_stock","nex7/out_stock/firmware_packed.dat"), ("out_stock99","nex7/out_stock99/firmware_packed.dat"), ("out_jpeg_v2","nex7/out_jpeg_v2/firmware_packed.dat")]:
    d = open(p,"rb").read()
    i = d.find(b"UDTRFIRM")
    if i < 0:
        print(name, "no UDTRFIRM"); continue
    magic = d[i:i+8]
    checksum = struct.unpack_from("<I", d, i+8)[0]
    ver = d[i+12:i+16]
    mode = d[i+16:i+17]
    luw = d[i+20:i+21]
    vmin, vmaj = d[i+32], d[i+33]
    model, region = struct.unpack_from("<II", d, i+36)
    fw_off, fw_size, nfs = struct.unpack_from("<III", d, i+44)
    print(name, "mode", mode, "ver", ver, "verMajor/minor", vmaj, vmin, "model", hex(model), "region", hex(region), "fw", fw_off, fw_size, "nfs", nfs)
