import sys
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile
p = "nex7/initrd_unpacked/sbin/init"
with open(p,"rb") as f:
    e = ELFFile(f)
    s = e.get_section_by_name(".symtab")
    for sym in s.iter_symbols():
        if sym.name.startswith("check_") or "mode" in sym.name:
            print(sym.name, hex(sym["st_value"]), sym["st_size"])
