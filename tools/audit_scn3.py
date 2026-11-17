import sys, os, re
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile

p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/bin/scenario.elf"
print("size", os.path.getsize(p))
with open(p, "rb") as f:
    e = ELFFile(f)
    print("type", e.header.e_type, "machine", e.header.e_machine)
    for seg in e.iter_segments():
        if seg.header.p_type == "PT_INTERP":
            print("INTERP:", seg.get_interp_name())
    dyn = e.get_section_by_name(".dynamic")
    strs = e.get_section_by_name(".dynstr").data()
    needed = [strs[t.entry.d_val:].split(b"\x00")[0].decode() for t in dyn.iter_tags() if t.entry.d_tag == "DT_NEEDED"]
    print("NEEDED:", needed)
    und = sorted({s.name for s in e.get_section_by_name(".dynsym").iter_symbols()
                  if s.name and s["st_shndx"] == "SHN_UNDEF"})
    print("UNDEF (%d):" % len(und))
    for u in und:
        print("   ", u)

d = open(p, "rb").read()
print("\n-- strings 相关 --")
for m in re.finditer(rb"[ -~]{4,}", d):
    s = m.group()
    if any(k in s for k in (b"scenario", b"sid", b"dlopen", b"so", b"chk", b"crc", b"sign", b"load")):
        print(hex(m.start()), s[:90].decode("latin1"))
