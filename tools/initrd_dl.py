import sys
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile
for name in ["libsonyc.so","sonyld.so","libsonydl.so"]:
    p = "nex7/initrd_unpacked/lib/" + name
    try:
        with open(p,"rb") as f:
            e = ELFFile(f)
            ds = e.get_section_by_name(".dynsym")
            hits = [s.name for s in ds.iter_symbols() if s.name in ("dlopen","dlsym","dlerror") and s["st_value"] != 0]
            print(name, "exports", hits)
    except Exception as ex:
        print(name, "err", ex)
