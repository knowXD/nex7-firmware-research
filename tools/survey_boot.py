import os, re, struct, sys
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile

base = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked"

def describe(p):
    d = open(p, "rb").read()
    tag = "?"
    extra = ""
    if d[:4] == b"\x7fELF":
        try:
            e = ELFFile(open(p, "rb"))
            tag = "ELF %s %s" % (e.header.e_type, e.header.e_machine)
            extra = "entry=0x%x phnum=%d" % (e.header.e_entry, e.header.e_phnum)
            need = []
            dyn = e.get_section_by_name(".dynamic")
            if dyn:
                strs = e.get_section_by_name(".dynstr").data()
                need = [strs[t.entry.d_val:].split(b"\x00")[0].decode() for t in dyn.iter_tags() if t.entry.d_tag == "DT_NEEDED"]
            extra += " NEEDED=%s" % need
        except Exception as ex:
            extra = repr(ex)
    else:
        tag = "raw magic=" + d[:8].hex()
    strs = [m.group().decode("latin1") for m in re.finditer(rb"[ -~]{6,}", d)][:14]
    print("== %s (%d B)" % (os.path.basename(p), len(d)))
    print("   ", tag, extra)
    for s in strs:
        print("      ", s[:80])

print("### sabin 目录 ###")
sd = os.path.join(base, "sabin")
for f in sorted(os.listdir(sd)):
    describe(os.path.join(sd, f))

print("\n### pformat3.elf ###")
describe("nex7/unpacked/updater.img_unpacked/bin/pformat3.elf")

print("\n### unidrv 模块 ###")
for f in ["unidrv1.ko", "unidrv2.ko"]:
    p = os.path.join("nex7/initrd_unpacked/kmod", f)
    d = open(p, "rb").read()
    print("== %s (%d B)" % (f, len(d)))
    for kw in [b"nflasha", b"bad", b"bbt", b"nand", b"erase", b"partition", b"block"]:
        print("    %-10s x%d" % (kw.decode(), d.count(kw)))
    hits = [m.group().decode("latin1") for m in re.finditer(rb"[ -~]{8,}", d)]
    keep = [s for s in hits if any(k in s.lower() for k in ("nand", "flash", "bad", "block", "erase", "part"))][:12]
    for s in keep:
        print("      ", s[:90])
