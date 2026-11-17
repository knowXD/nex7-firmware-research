import sys
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/initrd.img_unpacked/kmod/liro.ko"
with open(p,"rb") as f:
    e = ELFFile(f)
    print("type", e.header.e_type, "machine", e.header.e_machine)
    symtab = e.get_section_by_name(".symtab")
    if symtab:
        for s in symtab.iter_symbols():
            if s["st_info"]["type"] == "STT_FUNC" and s["st_value"]:
                print(hex(s["st_value"]), s["st_size"], s.name)
