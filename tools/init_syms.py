import sys
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile
p = "nex7/initrd_unpacked/sbin/init"
with open(p,"rb") as f:
    e = ELFFile(f)
    for sec in [".symtab", ".dynsym"]:
        s = e.get_section_by_name(sec)
        if not s:
            print(sec, "absent"); continue
        for sym in s.iter_symbols():
            if "parse" in sym.name or "env" in sym.name.lower() or "loop" in sym.name:
                print(sec, sym.name, hex(sym["st_value"]), sym["st_size"])
