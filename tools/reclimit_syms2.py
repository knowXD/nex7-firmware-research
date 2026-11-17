import sys
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile
for p in ["nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/lib/libmpr.so",
          "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/lib/libObj.so"]:
    print("==", p.split("/")[-1])
    with open(p,"rb") as f:
        e = ELFFile(f)
        for sec in [".dynsym", ".symtab"]:
            s = e.get_section_by_name(sec)
            if not s: continue
            for sym in s.iter_symbols():
                if "RecLimit" in sym.name or "RecLimitTime" in sym.name:
                    print(sec, sym.name, hex(sym["st_value"]), sym["st_size"])
