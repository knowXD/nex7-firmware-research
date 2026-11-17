import struct
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p, "rb").read()
n = len(d) - 2

def hw(o): return d[o] | (d[o+1] << 8)

cands = []
for o in range(0, n, 2):
    h = hw(o)
    # ADD pc, Rm  (0x4400 | Rm<<3 | 0xF)
    if (h & 0xFFC0) != 0x4400 or (h & 7) != 7:
        continue
    # 往前找 ADR 与 ldrb [r,r]
    adr_off = None; tbl = None
    for back in range(2, 17, 2):
        o2 = o - back
        h2 = hw(o2)
        if (h2 & 0xF800) == 0xA000:
            adr_off = o2
            tbl = ((o2 + 4) & ~3) + (h2 & 0xFF) * 4
            break
    if adr_off is None or tbl is None or tbl >= len(d):
        continue
    # 检查跳转表内容是否像"节数递增的字节偏移"
    tbl_bytes = d[tbl:tbl+20]
    if len(tbl_bytes) < 16:
        continue
    ok = all(tbl_bytes[i] < 0x80 for i in range(16))
    cands.append((o, adr_off, tbl, tbl_bytes[:16].hex()))

print("ADD pc 跳转候选:", len(cands))
for o, a, t, b in cands[:25]:
    print("  指令 0x%06X ADR@0x%06X 表@0x%06X bytes=%s" % (o, a, t, b))
