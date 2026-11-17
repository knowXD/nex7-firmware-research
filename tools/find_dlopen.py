import sys, os
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile
root = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/lib"
for fn in sorted(os.listdir(root)):
    if not fn.endswith(".so"): continue
    p = os.path.join(root, fn)
    try:
        with open(p,"rb") as f:
            e = ELFFile(f)
            ds = e.get_section_by_name(".dynsym")
            if not ds: continue
            for s in ds.iter_symbols():
                if s.name in ("dlopen","dlsym") and s["st_value"] != 0:
                    print(fn, s.name, hex(s["st_value"]))
    except Exception:
        pass
