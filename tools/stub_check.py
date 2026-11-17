import sys
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile
p = "nex7/hack/scn_stub2.so"
with open(p,"rb") as f:
    e = ELFFile(f)
    print("machine", e.header.e_machine, "type", e.header.e_type, "entry", hex(e.header.e_entry))
    dyn = e.get_section_by_name(".dynamic")
    tags = [(t.entry.d_tag, hex(t.entry.d_val)) for t in dyn.iter_tags()]
    print("dynamic tags", tags)
    ds = e.get_section_by_name(".dynsym")
    for s in ds.iter_symbols():
        if s.name:
            print("sym", s.name, hex(s["st_value"]), s["st_size"], "shndx", s["st_shndx"])
