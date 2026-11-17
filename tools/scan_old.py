import os, glob
for p in glob.glob("nex7/fw101/**/*", recursive=True) + glob.glob("nex7/fw102/**/*", recursive=True):
    if os.path.isfile(p):
        print(p, os.path.getsize(p))
print("---- scan ----")
for p in glob.glob("nex7/fw101/**/*.exe", recursive=True) + glob.glob("nex7/fw102/**/*.exe", recursive=True):
    d = open(p, "rb").read()
    print(os.path.basename(p), len(d))
    for tag in [b"UDTRFIRM", b"DATV", b"PROV", b"UDID", b"FDAT", b"DEND", bytes.fromhex("895546550d0a1a0a")]:
        print("  ", tag, d.find(tag))
