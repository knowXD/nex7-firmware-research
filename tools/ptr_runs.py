import struct
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p,"rb").read()
runs = []
i = 0
n = len(d) - 4
while i < n:
    w = struct.unpack_from("<I", d, i)[0]
    if 0xC3000000 <= w <= 0xC3FFFFFF:
        j = i
        cnt = 0
        while j < n:
            w2 = struct.unpack_from("<I", d, j)[0]
            if 0xC3000000 <= w2 <= 0xC3FFFFFF:
                cnt += 1; j += 4
            else:
                break
        if cnt >= 16:
            runs.append((i, cnt))
        i = j
    else:
        i += 4
runs.sort(key=lambda x: -x[1])
print("runs >=16 pointers:", len(runs))
for off, cnt in runs[:15]:
    print(hex(off), cnt, "first:", hex(struct.unpack_from("<I", d, off)[0]))
