import sys, struct
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/bin/im.elf"
with open(p,"rb") as f:
    e = ELFFile(f)
    for sec in e.iter_sections():
        if sec.name in (".rel.dyn",".rel.plt"):
            print("sec", sec.name, hex(sec.header.sh_addr), sec.num_relocations())
            for r in sec.iter_relocations():
                off = r["r_offset"]; add = r["r_addend"] if r.is_RELA() else None
                if add is not None and 0x3800 <= add <= 0x5300:
                    print("  got", hex(off), "->", hex(add), r["r_info_type"])
