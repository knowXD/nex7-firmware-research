p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p, "rb").read()
n = len(d) - 2
def hw(o): return d[o] | (d[o+1] << 8)

out = []
for o in range(0, n, 2):
    h = hw(o)
    if (h & 0xFF07) != 0x4407: continue
    adr_off = tbl = None
    for back in range(2, 21, 2):
        h2 = hw(o - back)
        if (h2 & 0xF800) == 0xA000:
            adr_off = o - back
            tbl = ((adr_off + 4) & ~3) + (h2 & 0xFF) * 4
            break
    if tbl is None or tbl >= len(d): continue
    # 找附近的 cmp rX, #0xE/0xF
    limit = None
    for back in range(4, 15, 2):
        o2 = adr_off - back
        h2 = hw(o2)
        if (h2 & 0xF800) == 0x2800:
            limit = h2 & 0xFF
            break
    if limit is None or limit not in (0xE, 0xF, 0x10):
        continue
    out.append((o, tbl, limit, d[tbl:tbl+16].hex()))

print("限位 0xE/0xF 的跳转表候选:", len(out))
for o, t, lim, b in out[:20]:
    print("  addpc@0x%06X 表@0x%06X limit=0x%X bytes=%s" % (o, t, lim, b))
