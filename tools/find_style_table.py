import struct, array, time
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p, "rb").read()
n = len(d) // 4
u = array.array("I")
u.frombytes(d[:n*4])

STR = [0x31E71C, 0x31E724, 0x31E730, 0x31E73C, 0x31E74C, 0x31E754, 0x31E75C,
       0x31E764, 0x31E76C, 0x31E778, 0x31E788, 0x31E790, 0x31E798]
t0 = time.time()
found = []
for stride_words in (1, 2, 3, 4):
    for i in range(0, n - (len(STR) - 1) * stride_words - 1):
        base = u[i] - STR[0]
        if base > 0x80000000:
            continue
        ok = True
        for k in range(1, 4):
            if u[i + k * stride_words] != (STR[k] + base) & 0xFFFFFFFF:
                ok = False
                break
        if not ok:
            continue
        for k in range(4, len(STR)):
            if u[i + k * stride_words] != (STR[k] + base) & 0xFFFFFFFF:
                ok = False
                break
        if ok:
            found.append((i*4, stride_words, base))
    print("stride %d 完成 %.1fs, 累计命中 %d" % (stride_words, time.time()-t0, len(found)))
for off, st, base in found[:10]:
    print("  表在 0x%06X stride=%d 基址差值=0x%X" % (off, st*4, base))
print("总计命中", len(found))
