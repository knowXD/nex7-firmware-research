import struct
p = "nex7/fw101/Sony_Update_NEX7V101/Sony_Update_NEX7V101.exe"
d = open(p,"rb").read()
print("file size", len(d))
pe = d.find(b"PE\x00\x00")
print("PE at", hex(pe))
nsec = struct.unpack_from("<H", d, pe+6)[0]
opt = pe+24
sizeopt = struct.unpack_from("<H", d, pe+20)[0]
sectab = pe+24+sizeopt
print("sections", nsec)
for i in range(nsec):
    off = sectab + i*40
    name = d[off:off+8].rstrip(b"\x00").decode("latin1")
    rawsize = struct.unpack_from("<I", d, off+16)[0]
    rawptr = struct.unpack_from("<I", d, off+20)[0]
    print(" ", name, "rawsize", hex(rawsize), "rawptr", hex(rawptr), "end", hex(rawptr+rawsize), "ok", rawptr+rawsize <= len(d))
print("PK eocd", d.find(b"PK\x05\x06"))
print("tail", d[-16:].hex())
