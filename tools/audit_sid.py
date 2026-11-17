import sys, os, glob
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile

base = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked"
print("== 各 scenario 模块里 sid / scenario_run 的地址与所在段 ==")
for p in sorted(glob.glob(base + "/scenario/*.so")):
    with open(p, "rb") as f:
        e = ELFFile(f)
        vals = {}
        for s in e.get_section_by_name(".dynsym").iter_symbols():
            if s.name in ("sid", "scenario_run") and s["st_shndx"] != "SHN_UNDEF":
                vals[s.name] = (s["st_value"], s["st_size"])
        loads = [(seg.header.p_vaddr, seg.header.p_vaddr + seg.header.p_filesz, seg.header.p_flags)
                 for seg in e.iter_segments() if seg.header.p_type == "PT_LOAD"]
        def seg_of(v):
            for a, b, fl in loads:
                if a <= v < b:
                    return "0x%x-0x%x(%s)" % (a, b, fl)
            return "?"
        sid = vals.get("sid")
        run = vals.get("scenario_run")
        print("%-38s size=%-6d sid=%-8s %-14s run=%-8s" % (
            os.path.basename(p), os.path.getsize(p),
            hex(sid[0]) if sid else "-", seg_of(sid[0]) if sid else "-",
            hex(run[0]) if run else "-"))

print()
print("== 哪些二进制里出现字符串 'sid'（可能是 dlsym 参数）==")
for root, dirs, files in os.walk(base):
    for fn in files:
        p = os.path.join(root, fn)
        try:
            d = open(p, "rb").read()
        except Exception:
            continue
        n = d.count(b"sid\x00")
        n2 = d.count(b"\"sid\"")
        if n or n2:
            print("%-50s 'sid\\0'x%d" % (os.path.relpath(p, base), n))
