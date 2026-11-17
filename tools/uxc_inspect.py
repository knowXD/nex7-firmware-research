import os, struct
root = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/share/app"
files = []
for f in os.listdir(root):
    p = os.path.join(root, f)
    if os.path.isfile(p):
        files.append((f, os.path.getsize(p)))
for f, s in sorted(files)[:40]:
    print(f, s)
print("total", len(files))
p = os.path.join(root, "string_english.uxc")
d = open(p,"rb").read()
print("magic", d[:16].hex(), d[:16])
