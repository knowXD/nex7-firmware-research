import struct, time
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p, "rb").read()
TARGET_LO, TARGET_HI = 0x31E700, 0x31E7B0
t0 = time.time()
hits = []
n = len(d) - 2
for o in range(0, n, 2):
    hw = d[o] | (d[o+1] << 8)
    if (hw & 0xF800) != 0xA000:      # Thumb ADR: ADD Rd, PC, #imm8*4
        continue
    imm = (hw & 0xFF) * 4
    pc = (o + 4) & ~3
    t = pc + imm
    if TARGET_LO <= t <= TARGET_HI:
        hits.append((o, hw, t))
print("耗时 %.1fs，ADR 命中 %d 处" % (time.time()-t0, len(hits)))
for o, hw, t in hits[:20]:
    print("  0x%06X hw=0x%04X -> 0x%06X" % (o, hw, t))
