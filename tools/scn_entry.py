import sys
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/scenario/AVBB_SCN_START_VIDEO.so"
with open(p,"rb") as f:
    e = ELFFile(f)
    for sec in [".dynsym",".symtab"]:
        s = e.get_section_by_name(sec)
        if not s: continue
        for sym in s.iter_symbols():
            if sym.name in ("scenario_run","testcmd_run_scenario"):
                print(sec, sym.name, hex(sym["st_value"]), sym["st_size"])
    # disassemble scenario_run via r2 later
