import sys, os, re
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile
base = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/lib"
for fn in ["libmpr.so", "libObj.so"]:
    p = os.path.join(base, fn)
    with open(p, "rb") as f:
        e = ELFFile(f)
        dyn = e.get_section_by_name(".dynsym")
        names = [s.name for s in dyn.iter_symbols()] if dyn else []
        hits = [n for n in names if any(k in n.lower() for k in ["quality","qscale","encodestill","jpg","jpeg","encode"])]
        print("==", fn, "dynsym", len(names), "hits", len(hits))
        for n in sorted(set(hits))[:30]:
            print("   ", n)
    d = open(p, "rb").read()
    for kw in [b"Quality", b"quality", b"qscale", b"Qscale", b"JPEG_QUALITY", b"JPG_QUALITY"]:
        cnt = d.count(kw)
        if cnt:
            print("   str", kw, cnt, hex(d.find(kw)))
