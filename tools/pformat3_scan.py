import sys, re
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile

p = "nex7/unpacked/updater.img_unpacked/bin/pformat3.elf"
d = open(p, "rb").read()
print("size", len(d))
with open(p, "rb") as f:
    e = ELFFile(f)
    print("type", e.header.e_type, "entry 0x%x" % e.header.e_entry)
    sym = e.get_section_by_name(".symtab")
    print("symtab:", "yes" if sym else "NO")
    if sym:
        ns = [(s.name, s["st_value"], s["st_size"]) for s in sym.iter_symbols() if s.name]
        print("symbols:", len(ns))
        for n, v, s in ns[:40]:
            print("   %-32s 0x%06x %d" % (n, v, s))
    dyn = e.get_section_by_name(".dynsym")
    if dyn:
        print("\ndynsym:", [s.name for s in dyn.iter_symbols() if s.name][:25])
    print("\nsegments:")
    for seg in e.iter_segments():
        print("   %-10s vaddr=0x%06x filesz=0x%x" % (seg.header.p_type, seg.header.p_vaddr, seg.header.p_filesz))

print("\n== 全部字符串 ==")
strs = []
for m in re.finditer(rb"[ -~]{5,}", d):
    s = m.group().decode("latin1")
    if s not in strs:
        strs.append(s)
for s in strs[:120]:
    print("  ", s[:100])
