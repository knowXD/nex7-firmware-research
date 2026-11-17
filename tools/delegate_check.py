import sys
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile
p = "nex7/hack/scn_delegate.so"
with open(p,"rb") as f:
    e = ELFFile(f)
    print("type", e.header.e_type, "entry", hex(e.header.e_entry))
    dyn = e.get_section_by_name(".dynamic")
    print([ (t.entry.d_tag, hex(t.entry.d_val)) for t in dyn.iter_tags() ])
    for s in e.get_section_by_name(".dynsym").iter_symbols():
        if s.name:
            print("sym", s.name, hex(s["st_value"]), s["st_size"], "undef" if s["st_shndx"]=="SHN_UNDEF" else "")
