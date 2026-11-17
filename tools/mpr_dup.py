import os, re, hashlib
roots = ["nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked",
         "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked"]
print("### libmpr 副本 ###")
for r in roots:
    for root, dirs, files in os.walk(r):
        for fn in files:
            if "mpr" in fn.lower():
                p = os.path.join(root, fn)
                h = hashlib.sha256(open(p, "rb").read()).hexdigest()[:16]
                print("   %-70s %8d %s" % (p.split("dev\\\\")[-1], os.path.getsize(p), h))

av = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(av, "rb").read()
print("\n### av-cam.bin 里的 hdAvcIfo / IFO 相关字符串 ###")
seen = set()
for m in re.finditer(rb"[ -~]{6,}", d):
    s = m.group().decode("latin1")
    if re.search(r"hdAvcIfo|Ifo|IFO", s) and s not in seen:
        seen.add(s); print("   ", s[:100])
print("\n### av-cam 里成组的码率常数（0x0F97E0 附近）###")
import struct
for off in (0x0F97E0, 0x35B730, 0x2B7A10):
    vals = struct.unpack_from("<8I", d, off-16)
    print("   0x%06X:" % (off-16), " ".join("%d(0x%X)" % (v, v) for v in vals))
