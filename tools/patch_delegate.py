stub = open("nex7/hack/scn_delegate2.so","rb").read()
ORIG = 11516
padded = stub + b"\x00" * (ORIG - len(stub))
open("nex7/hack/scn_delegate_padded.so","wb").write(padded)
src = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked"
data = bytearray(open(src,"rb").read())
data[0xD1C400:0xD1C400+ORIG] = padded
open("nex7/work_n8_delegate.img","wb").write(data)
print("stub", len(stub), "padded", len(padded), "patched at 0xD1C400")
