import sys, re
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/lib/libpro00.so"
d = open(p,"rb").read()
print("size", len(d))
for m in re.finditer(rb"[\x20-\x7e]{4,}", d):
    print("  str", hex(m.start()), m.group().decode("latin1")[:100])
with open(p,"rb") as f:
    e = ELFFile(f)
    for sec in [".dynsym"]:
        s = e.get_section_by_name(sec)
        if s:
            for sym in s.iter_symbols():
                if sym.name and sym["st_value"] != 0:
                    print("  sym", sym.name, hex(sym["st_value"]), sym["st_size"])
