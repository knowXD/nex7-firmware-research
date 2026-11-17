import sys
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/scenario/AVBB_SCN_START_VIDEO.so"
with open(p,"rb") as f:
    e = ELFFile(f)
    # find section containing 0x94fc
    for s in e.iter_sections():
        a = s["sh_addr"]; sz = s["sh_size"]
        if a <= 0x94fc < a+sz:
            off = s["sh_offset"] + (0x94fc - a)
            f.seek(off); data = f.read(8)
            print("sid section", s.name, "bytes", data.hex())
