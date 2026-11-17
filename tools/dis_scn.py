import sys
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile
from capstone import *

p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/scenario/AVBB_SCN_START_VIDEO.so"
with open(p,"rb") as f:
    e = ELFFile(f)
    syms = {}
    for sec in [".symtab",".dynsym"]:
        s = e.get_section_by_name(sec)
        if not s: continue
        for sym in s.iter_symbols():
            if sym.name:
                syms[sym.name] = (sym["st_value"], sym["st_size"])
    text = e.get_section_by_name(".text")
    tdata = text.data(); taddr = text["sh_addr"]
addr, size = syms["scenario_run"]
off = addr - taddr
codeb = tdata[off:off+size+8]
md = Cs(CS_ARCH_ARM, CS_MODE_THUMB)
md.detail = False
for ins in md.disasm(codeb, addr):
    print("%08x  %-8s %s %s" % (ins.address, ins.bytes.hex(), ins.mnemonic, ins.op_str))
