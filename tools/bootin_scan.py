import sys, re
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/bin/bootin.elf"
d = open(p,"rb").read()
print("size", len(d))
for m in re.finditer(rb"[\x20-\x7e]{4,}", d):
    print(hex(m.start()), m.group().decode("latin1")[:110])
with open(p,"rb") as f:
    e = ELFFile(f)
    for sec in [".symtab",".dynsym"]:
        s = e.get_section_by_name(sec)
        if not s: continue
        print("== syms", sec)
        for sym in s.iter_symbols():
            if sym.name and sym["st_value"] != 0 and (sym["st_size"] or "main" in sym.name or "init" in sym.name):
                print("  ", sym.name, hex(sym["st_value"]), sym["st_size"])
