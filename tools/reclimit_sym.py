import sys
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/lib/libmpr.so"
with open(p,"rb") as f:
    e = ELFFile(f)
    dyn = e.get_section_by_name(".dynsym")
    for s in dyn.iter_symbols():
        if "RecLimit" in s.name or "RecLimitTime" in s.name:
            print(s.name, hex(s["st_value"]), s["st_size"])
