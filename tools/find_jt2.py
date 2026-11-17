p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p, "rb").read()
n = len(d) - 2
def hw(o): return d[o] | (d[o+1] << 8)

cands = []
for o in range(0, n, 2):
    h = hw(o)
    # 高位寄存器 ADD pc, Rm: 010001 00 H1 H2 Rm Rd, Rd=15
    if (h & 0xFF07) != 0x4407:
        continue
    rn = (h >> 3) & 7
    adr_off = None; tbl = None
    for back in range(2, 21, 2):
        o2 = o - back
        h2 = hw(o2)
        if (h2 & 0xF800) == 0xA000:
            adr_off = o2
            tbl = ((o2 + 4) & ~3) + (h2 & 0xFF) * 4
            break
    if tbl is None or tbl >= len(d): continue
    tb = d[tbl:tbl+16]
    if len(tb) < 16: continue
    cands.append((o, adr_off, tbl, tb.hex(), rn))

print("候选:", len(cands))
for o, a, t, b, rn in cands[:30]:
    print("  addpc@0x%06X ADR@0x%06X 表@0x%06X Rm=%d bytes=%s" % (o, a, t, rn, b))
