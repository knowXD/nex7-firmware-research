import re
paths = {
 "1.01":"nex7/fw101/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/vmlinux.bin",
 "1.03":"nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/vmlinux.bin",
}
a = open(paths["1.01"],"rb").read(); b = open(paths["1.03"],"rb").read()
print("sizes", len(a), len(b))
diff = [i for i in range(min(len(a),len(b))) if a[i]!=b[i]]
print("diff bytes", len(diff))
regions=[]
for i in diff:
    if regions and i-regions[-1][1] <= 32: regions[-1][1]=i
    else: regions.append([i,i])
print("regions", len(regions))
for r in regions[:10]:
    print("  ", hex(r[0]), "-", hex(r[1]), "len", r[1]-r[0]+1)
print("--- TPZL/cmpr strings ---")
for k in [b"TPZL", b"tpzl", b"lzpt", b"cmpr", b"wbi_lzp", b"cmpr_lz", b"lz77_inflate"]:
    print(k, a.find(k), b.find(k))
