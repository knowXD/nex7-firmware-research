import sys, shutil
sys.path.append("nex7/pylibs")
from elftools.elf.elffile import ELFFile
stub = open("nex7/hack/scn_stub.so","rb").read()
print("stub size", len(stub))
# verify exports
with open("nex7/hack/scn_stub.so","rb") as f:
    e = ELFFile(f)
    for s in e.get_section_by_name(".dynsym").iter_symbols():
        if s.name:
            print("export", s.name, hex(s["st_value"]), s["st_size"])
# pad to original size
ORIG = 11516
assert len(stub) <= ORIG
padded = stub + b"\x00" * (ORIG - len(stub))
open("nex7/hack/scn_stub_padded.so","wb").write(padded)
print("padded", len(padded))
# patch image copy
src = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked"
dst = "nex7/work_n8_scn.img"
d = bytearray(open(src,"rb").read())
off = 0xD1C400
print("old bytes", d[off:off+8].hex())
d[off:off+ORIG] = padded
open(dst,"wb").write(d)
print("new bytes", d[off:off+8].hex())
