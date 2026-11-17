import struct, array, time
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p, "rb").read()
n = len(d) // 2
a = array.array("h")
a.frombytes(d[:n*2])
t0 = time.time()
cands = []
for i in range(n - 9):
    r0 = a[i] + a[i+1] + a[i+2]
    if not (900 <= r0 <= 4600):
        continue
    r1 = a[i+3] + a[i+4] + a[i+5]
    r2 = a[i+6] + a[i+7] + a[i+8]
    if abs(r1 - r0) <= 64 and abs(r2 - r0) <= 64:
        if a[i] > 200 and a[i+4] > 200 and a[i+8] > 200:
            cands.append((i*2, r0, list(a[i:i+9])))
print("耗时 %.1fs，候选 %d 组" % (time.time()-t0, len(cands)))
for off, s, vals in cands[:12]:
    print("  0x%06X rows=%d %s" % (off, s, vals))
