import sys, re
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/bin/sen.elf"
with open(p,"rb") as f:
    e = ELFFile(f)
    for sec in [".symtab", ".dynsym"]:
        s = e.get_section_by_name(sec)
        if not s: continue
        print("== ", sec)
        for sym in s.iter_symbols():
            n = sym.name
            if n and (sym["st_size"] or n in ("main","_start")):
                print("  ", n, hex(sym["st_value"]), sym["st_size"])
