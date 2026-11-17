import os, glob
print("== 1.02 unpacked ==")
for p in sorted(glob.glob("nex7/fw102/unpacked/*")):
    print(p, os.path.getsize(p) if os.path.isfile(p) else "<dir>")
cfg = "nex7/fw102/unpacked/config.yaml"
if os.path.exists(cfg):
    print(open(cfg).read()[:400])
print("== 1.01 exe header ==")
d = open("nex7/fw101/Sony_Update_NEX7V101/Sony_Update_NEX7V101.exe","rb").read(4096)
print(d[:16].hex(" "))
for sig in [b"PK\x03\x04", b"MSCF", b"7z\xbc\xaf\x27\x1c", b"Rar!", b"MSI"]:
    print(sig, open("nex7/fw101/Sony_Update_NEX7V101/Sony_Update_NEX7V101.exe","rb").read().find(sig))
