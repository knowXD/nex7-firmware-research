import struct
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p, "rb").read()
base = 0x455E00
vals = struct.unpack_from("<64h", d, base)
print("0x%06X 起 64 个 int16:" % base)
for i in range(0, 64, 8):
    print("  +0x%03X" % (i*2), vals[i:i+8])
print("\n按 9 个一组看（从 0x455E2E 开始）:")
off = 0x455E2E
for k in range(6):
    g = struct.unpack_from("<9h", d, off + k*18)
    print("  #%d 0x%06X %s  rowsum=%d,%d,%d" % (k, off+k*18, g, sum(g[0:3]), sum(g[3:6]), sum(g[6:9])))
