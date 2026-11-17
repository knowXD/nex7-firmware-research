import sys, os
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile
base = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/lib"
for fn in ["libmpr.so", "libObj.so"]:
    p = os.path.join(base, fn)
    if not os.path.exists(p):
        print(fn, "missing"); continue
    print("==", fn, os.path.getsize(p))
    with open(p, "rb") as f:
        e = ELFFile(f)
        sym = e.get_section_by_name(".symtab")
        names = []
        if sym:
            for s in sym.iter_symbols():
                n = s.name
                if any(k in n.lower() for k in ["quality","qscale","encodestill","jpg","jpeg"]):
                    names.append(n)
        print("  symbols matching:", len(names))
        for n in sorted(set(names))[:40]:
            print("   ", n)
