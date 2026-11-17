import sys, os
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile

def exports(p):
    print("== %s (%d B)" % (os.path.basename(p), os.path.getsize(p)))
    with open(p, "rb") as f:
        e = ELFFile(f)
        symtab = e.get_section_by_name(".dynsym")
        if symtab is None:
            print("   no .dynsym"); return
        rows = []
        for s in symtab.iter_symbols():
            if not s.name: continue
            defined = s["st_shndx"] != "SHN_UNDEF"
            rows.append((s.name, "DEF" if defined else "UND", hex(s["st_value"]), s["st_size"]))
        for r in rows:
            print("   %-22s %-4s %-10s %d" % r)

base = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/scenario/"
exports(base + "AVBB_SCN_START_VIDEO.so")
exports(base + "CAMERA_SCN_MOVIE_REC_START.so")
for p in ["nex7/hack/scn_stub.so", "nex7/hack/scn_stub_padded.so", "nex7/hack/scn_delegate_padded.so"]:
    exports(p)

print("\n== 两个 nflasha8 镜像对比 ==")
a = open("nex7/work_n8_delegate.img","rb").read()
b = open("nex7/work_n8_scn.img","rb").read()
print("sizes", len(a), len(b), "equal-len", len(a)==len(b))
if len(a)==len(b):
    diffs = [i for i in range(len(a)) if a[i]!=b[i]]
    print("diff bytes:", len(diffs))
    if diffs:
        print("first 0x%X last 0x%X" % (diffs[0], diffs[-1]))
        lo, hi = 0xD1C400, 0xD1C400+11516
        inside = sum(1 for d in diffs if lo <= d < hi)
        print("inside stub window [0x%X,0x%X): %d / %d" % (lo, hi, inside, len(diffs)))
