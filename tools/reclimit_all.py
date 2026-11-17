import sys, os
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile
root = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/lib"
for fn in sorted(os.listdir(root)):
    p = os.path.join(root, fn)
    if not fn.endswith(".so"): continue
    try:
        with open(p,"rb") as f:
            e = ELFFile(f)
            defs = []
            for sec in [".dynsym", ".symtab"]:
                s = e.get_section_by_name(sec)
                if not s: continue
                for sym in s.iter_symbols():
                    if "RecLimit" in sym.name and sym["st_value"] != 0:
                        defs.append((sec, sym.name, hex(sym["st_value"]), sym["st_size"]))
            if defs:
                print(fn, defs)
    except Exception as ex:
        pass
