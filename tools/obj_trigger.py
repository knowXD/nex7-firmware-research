import sys, struct
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile

p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/lib/libObj.so"
d = open(p, "rb").read()
with open(p, "rb") as f:
    e = ELFFile(f)
    segs = [(s.header.p_offset, s.header.p_vaddr, s.header.p_filesz) for s in e.iter_segments() if s.header.p_type == "PT_LOAD"]
print("size", len(d), "LOAD:", segs)

def vaddr_of(off):
    for po, va, sz in segs:
        if po <= off < po + sz: return va + (off - po)
    return None

for kw in [b"PARAMID_CAPTURE_START_TRIGGER", b"PARAMID_CAPTURE_ID", b"model/STILL_REC", b"MSGID_SET_DUALREC_CAPTURE_EXPAND_MODE_CMD"]:
    off = d.find(kw)
    print("\n%s: file=0x%X vaddr=%s" % (kw.decode(), off, hex(vaddr_of(off)) if off >= 0 else "-"))
    if off < 0: continue
    va = vaddr_of(off)
    pat = struct.pack("<I", va)
    refs = []
    i = d.find(pat)
    while i >= 0:
        refs.append(i); i = d.find(pat, i+1)
    print("   字面量引用:", [hex(r) for r in refs[:8]], "共", len(refs))
