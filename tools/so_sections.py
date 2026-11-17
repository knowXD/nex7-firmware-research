import sys
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile
p = "nex7/hack/scn_stub.so"
with open(p,"rb") as f:
    e = ELFFile(f)
    for s in e.iter_sections():
        print("%-20s %8x %8x" % (s.name, s["sh_offset"], s["sh_size"]))
