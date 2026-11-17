import sys, re
sys.path.append("nex7/pylibs")
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/bin/im.elf"
d = open(p, "rb").read()
print("size", len(d), "magic", d[:4])
i = d.find(b"av-cam")
print("av-cam ctx:", d[i-120:i+120])
from elftools.elf.elffile import ELFFile
with open(p, "rb") as f:
    e = ELFFile(f)
    print("type", e.header.e_type, "machine", e.header.e_machine, "entry", hex(e.header.e_entry))
    for s in e.iter_sections():
        print("  sec", s.name, hex(s.header.sh_addr), hex(s.header.sh_size))
