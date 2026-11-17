import sys
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/lib/libsencore.so"
with open(p,"rb") as f:
    e = ELFFile(f)
    for sec in [".symtab",".dynsym"]:
        s = e.get_section_by_name(sec)
        if not s: continue
        for sym in s.iter_symbols():
            n = sym.name
            if "Plugin" in n or "plugin" in n:
                print(sec, n, hex(sym["st_value"]), sym["st_size"])
