import sys, re
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile

p = "nex7/initrd_unpacked/kmod/unidrv1.ko"
with open(p, "rb") as f:
    e = ELFFile(f)
    print("sections:", [s.name for s in e.iter_sections()][:20])
    sym = e.get_section_by_name(".symtab")
    if sym is None:
        print("no .symtab")
    else:
        names = [(s.name, s["st_value"], s["st_size"]) for s in sym.iter_symbols() if s.name]
        print("symbols:", len(names))
        key = [n for n in names if re.search(r"nand|flash|bb|block|part|erase|read|write", n[0], re.I)]
        print("\n== 关键符号 (%d) ==" % len(key))
        for n, v, s in key[:60]:
            print("   %-42s 0x%08x %d" % (n, v, s))

d = open(p, "rb").read()
print("\n== bad/bbt 相关字符串上下文 ==")
for m in re.finditer(rb"[ -~]{6,}", d):
    s = m.group().decode("latin1")
    if re.search(r"bad|bbt|skip|logical|physical|remap|reserve", s, re.I):
        print("   ", s[:110])
