import sys, os
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile

def info(p):
    if not os.path.exists(p):
        print("  MISSING", p); return
    print("  == %s (%d B)" % (p, os.path.getsize(p)))
    with open(p, "rb") as f:
        e = ELFFile(f)
        h = e.header
        print("     type=%s machine=%s entry=0x%x phdrs=%d" % (h.e_type, h.e_machine, h.e_entry, h.e_phnum))
        try:
            dyn = e.get_section_by_name(".dynamic")
            strs = e.get_section_by_name(".dynstr").data()
            needed = []
            for t in dyn.iter_tags():
                if t.entry.d_tag == "DT_NEEDED":
                    needed.append(strs[t.entry.d_val:].split(b"\x00")[0].decode())
            print("     NEEDED:", needed if needed else "(none)")
        except Exception as ex:
            print("     dynamic:", ex)
        try:
            syms = []
            for s in e.get_section_by_name(".dynsym").iter_symbols():
                if s.name and s["st_shndx"] == "SHN_UNDEF":
                    syms.append(s.name)
            print("     undefined syms:", syms[:20], "..." if len(syms) > 20 else "")
        except Exception as ex:
            print("     dynsym:", ex)
        segs = []
        for seg in e.iter_segments():
            if seg.header.p_type == "PT_LOAD":
                segs.append("vaddr=0x%x filesz=0x%x flags=%s" % (seg.header.p_vaddr, seg.header.p_filesz, seg.header.p_flags))
        print("     LOAD:", segs)

base = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked"
cand = []
for root, dirs, files in os.walk(base):
    for fn in files:
        if "SCN" in fn.upper() and fn.lower().endswith(".so"):
            cand.append(os.path.join(root, fn))
print("originals found:", cand)
for c in cand[:3]:
    info(c)
print()
for p in ["nex7/hack/scn_delegate.so", "nex7/hack/scn_delegate2.so", "nex7/hack/scn_delegate_padded.so", "nex7/hack/scn_stub.so"]:
    info(p)
