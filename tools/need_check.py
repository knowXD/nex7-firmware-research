import sys
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile
p = "nex7/hack/scn_delegate2.so"
with open(p,"rb") as f:
    e = ELFFile(f)
    dyn = e.get_section_by_name(".dynamic")
    strtab = e.get_section_by_name(".dynstr").data()
    for t in dyn.iter_tags():
        if t.entry.d_tag == "DT_NEEDED":
            print("NEEDED", strtab[t.entry.d_val:].split(b"\x00")[0])
    for s in e.get_section_by_name(".dynsym").iter_symbols():
        if s.name:
            print("sym", s.name, hex(s["st_value"]), s["st_size"])
