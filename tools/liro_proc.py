import sys
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/initrd.img_unpacked/kmod/liro.ko"
with open(p,"rb") as f:
    e = ELFFile(f)
    for s in e.iter_sections():
        if s.header.sh_size:
            print("SEC", s.name, "addr", hex(s.header.sh_addr), "off", hex(s.header.sh_offset), "size", hex(s.header.sh_size))
    symtab = e.get_section_by_name(".symtab")
    for s in symtab.iter_symbols():
        if "proc" in s.name.lower() or "start" in s.name.lower():
            print("SYM", s.name, hex(s["st_value"]), s["st_size"], s["st_shndx"])
