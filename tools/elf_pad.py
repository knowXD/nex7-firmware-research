import sys, os, struct
sys.path.insert(0, "nex7/pylibs")
from elftools.elf.elffile import ELFFile

src, dst, size = sys.argv[1], sys.argv[2], int(sys.argv[3])
d = open(src, "rb").read()
if len(d) > size:
    sys.exit("stub too big: %d > %d" % (len(d), size))
out = d + b"\x00" * (size - len(d))
open(dst, "wb").write(out)

with open(dst, "rb") as f:
    e = ELFFile(f)
    maxend = 0
    for seg in e.iter_segments():
        if seg.header.p_type == "PT_LOAD":
            maxend = max(maxend, seg.header.p_vaddr + seg.header.p_filesz)
    syms = {s.name: (s["st_value"], s["st_size"]) for s in e.get_section_by_name(".dynsym").iter_symbols() if s.name}
    und = [n for n, v in syms.items() if v[0] == 0]
print("padded %d -> %d bytes; LOAD ends at 0x%X; exports=%s; undef=%s"
      % (len(d), len(out), maxend,
         {k: hex(v[0]) for k, v in syms.items() if v[0]}, und))
