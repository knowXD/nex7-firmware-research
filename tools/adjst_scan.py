import sys, re
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/bin/adjstctl.elf"
d = open(p,"rb").read()
print("size", len(d))
print("== strings with paths/libs")
for m in re.finditer(rb"[\x20-\x7e]{4,}", d):
    s = m.group().decode("latin1")
    if any(k in s for k in ["/usr","/setting",".so","dlopen","scenario","Scenario","SCN"]):
        print("  ", hex(m.start()), s[:110])
print("== symbols")
with open(p,"rb") as f:
    e = ELFFile(f)
    for sec in [".symtab",".dynsym"]:
        s = e.get_section_by_name(sec)
        if not s: continue
        for sym in s.iter_symbols():
            n = sym.name
            if n and sym["st_value"] != 0 and (sym["st_size"] or "scenario" in n.lower() or "dl" in n.lower()):
                print("  ", sec, n, hex(sym["st_value"]), sym["st_size"])
