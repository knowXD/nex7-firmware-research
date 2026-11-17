import sys
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile
for name in ["libsonyld.so","libsonydl.so","libsonyc.so"]:
    p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/lib/" + name
    with open(p,"rb") as f:
        e = ELFFile(f)
        ds = e.get_section_by_name(".dynsym")
        names = [s.name for s in ds.iter_symbols() if "dl" in s.name.lower()]
        print(name, names[:20])
