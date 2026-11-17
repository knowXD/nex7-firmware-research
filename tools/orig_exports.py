import sys
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/scenario/AVBB_SCN_START_VIDEO.so"
with open(p,"rb") as f:
    e = ELFFile(f)
    ds = e.get_section_by_name(".dynsym")
    for s in ds.iter_symbols():
        if s.name and s["st_value"] != 0:
            print("export", s.name, hex(s["st_value"]), s["st_size"])
