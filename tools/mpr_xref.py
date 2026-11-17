import sys, struct
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile

p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/lib/libmpr.so"
d = open(p, "rb").read()
with open(p, "rb") as f:
    e = ELFFile(f)
    print("type", e.header.e_type)
    segs = []
    for seg in e.iter_segments():
        if seg.header.p_type == "PT_LOAD":
            segs.append((seg.header.p_offset, seg.header.p_vaddr, seg.header.p_filesz))
            print("  LOAD off=0x%06X vaddr=0x%06X filesz=0x%X" % (seg.header.p_offset, seg.header.p_vaddr, seg.header.p_filesz))

def vaddr_of(off):
    for po, va, sz in segs:
        if po <= off < po + sz:
            return va + (off - po)
    return None

target_off = 0x4ED990
tv = vaddr_of(target_off)
print("\n0x%X 文件偏移 -> vaddr 0x%X" % (target_off, tv))

pat = struct.pack("<I", tv)
print("搜索字面量引用 vaddr...")
hits = []
i = d.find(pat)
while i >= 0:
    hits.append(i)
    i = d.find(pat, i+1)
print("命中", len(hits), "处:", [hex(h) for h in hits[:12]])

# 也找目标附近可能被引用的入口（表首地址）
for delta in (0, -0x10, -0x8):
    if tv + delta > 0:
        pat2 = struct.pack("<I", tv + delta)
        n = d.count(pat2)
        if n:
            print("  vaddr 0x%X 被引用 %d 次" % (tv + delta, n))
