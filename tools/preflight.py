import sys, os, io, struct, hashlib, tarfile
sys.path.append("nex7/pylibs"); sys.path.append("nex7/fwtool.py-master")
from fwtool.lz77 import inflateLz77

def tpzl_info(data):
    magic, bs, tocoff, tocsz = struct.unpack_from("<4sIII", data, 0)
    n = tocsz // 8
    off, size = struct.unpack_from("<II", data, tocoff)
    b = io.BytesIO(data[off:off+size]); read = 0; chunks = []
    while read < (1 << bs):
        c = len(inflateLz77(b)); chunks.append(c); read += c
        if len(chunks) > 32: break
    return magic, bs, n, chunks

print("== 1. 原始 firmware.tar ==")
tf = tarfile.open("nex7/unpacked/firmware.tar", "r:")
m = tf.getmember("0700_part_image/dev/nflasha3")
orig_img = tf.extractfile(m).read()
print("  nflasha3 size", m.size, "hash", hashlib.sha256(orig_img).hexdigest()[:16])
print("  tpzl", tpzl_info(orig_img)[:3], "block0 chunks", tpzl_info(orig_img)[3][:3])

print("== 2. JPEG 补丁 tar ==")
tf2 = tarfile.open("nex7/new_jpeg_v2.tar", "r:")
m2 = tf2.getmember("0700_part_image/dev/nflasha3")
new_img = tf2.extractfile(m2).read()
print("  nflasha3 size", m2.size, "hash", hashlib.sha256(new_img).hexdigest()[:16])
print("  tpzl", tpzl_info(new_img)[:3], "block0 chunks", tpzl_info(new_img)[3][:3])

print("== 3. sum 行校验 ==")
summ = tf2.extractfile(tf2.getmember("0701_part_image_sum/part_image.sum")).read().decode("latin1")
for line in summ.split("\n"):
    if line.endswith("dev/nflasha3,"):
        p = line.split(",")
        print("  sum crc", p[1], "size", p[2], "actual crc %08x" % (__import__("zlib").crc32(new_img) & 0xffffffff), "size %08x" % len(new_img))

print("== 4. 解压后 FAT 镜像对比 ==")
sys.path.append("nex7/fwtool.py-master")
from fwtool.archive import lzpt
uf = next(lzpt.readLzpt(io.BytesIO(new_img)))
fat_new = uf.contents.read()
fat_orig = open("nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked", "rb").read()
print("  new fat", len(fat_new), "orig fat", len(fat_orig))
diff = [i for i in range(min(len(fat_new), len(fat_orig))) if fat_new[i] != fat_orig[i]]
print("  diff bytes", len(diff), "first", hex(diff[0]) if diff else None, "last", hex(diff[-1]) if diff else None)

print("== 5. 包文件 ==")
for p in ["nex7/out_jpeg_v2/firmware_packed.dat", "nex7/out_stock99/firmware_packed.dat"]:
    print("  ", p, os.path.getsize(p) if os.path.exists(p) else "MISSING")
