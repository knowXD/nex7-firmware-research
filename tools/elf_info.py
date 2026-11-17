import sys, os
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile

p = sys.argv[1]
print("==", p, os.path.getsize(p))
with open(p, "rb") as f:
    e = ELFFile(f)
    print("  type", e.header.e_type, "machine", e.header.e_machine)
    dyn = e.get_section_by_name(".dynamic")
    strs = e.get_section_by_name(".dynstr").data()
    need = [strs[t.entry.d_val:].split(b"\x00")[0].decode() for t in dyn.iter_tags() if t.entry.d_tag == "DT_NEEDED"]
    print("  NEEDED:", need)
    und = [s.name for s in e.get_section_by_name(".dynsym").iter_symbols() if s.name and s["st_shndx"] == "SHN_UNDEF"]
    ex = [(s.name, hex(s["st_value"]), s["st_size"]) for s in e.get_section_by_name(".dynsym").iter_symbols()
          if s.name and s["st_shndx"] != "SHN_UNDEF"]
    print("  UND:", und)
    print("  EXP:", ex)
    for seg in e.iter_segments():
        if seg.header.p_type == "PT_LOAD":
            print("  LOAD vaddr=0x%x off=0x%x filesz=0x%x flags=%s" % (
                seg.header.p_vaddr, seg.header.p_offset, seg.header.p_filesz, seg.header.p_flags))
