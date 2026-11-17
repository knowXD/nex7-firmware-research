import tarfile, zlib
a = tarfile.open("nex7/unpacked/firmware.tar", "r:")
b = tarfile.open("nex7/new_jpeg_v2.tar", "r:")
ma = {m.name: m for m in a.getmembers() if m.isfile()}
mb = {m.name: m for m in b.getmembers() if m.isfile()}
print("members", len(ma), len(mb))
print("only in orig", set(ma)-set(mb))
print("only in new", set(mb)-set(ma))
diffs = []
for n in sorted(set(ma) & set(mb)):
    da = a.extractfile(ma[n]).read()
    db = b.extractfile(mb[n]).read()
    if da != db:
        diffs.append((n, len(da), len(db)))
print("differing members:")
for n, la, lb in diffs:
    print("  ", n, la, "->", lb)
