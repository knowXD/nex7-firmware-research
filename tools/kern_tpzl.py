a = open("nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/vmlinux.bin","rb").read()
for k in [b"IKCFG_ST", b"config.gz", b"/proc/config", b"cramfs", b"LZ77", b"zlib_inflate", b"unlz77", b"decompress"]:
    print(k, a.find(k))
i = a.find(b"TPZL")
seg = a[i-64:i+96]
print("TPZL hex:", seg.hex(" "))
print("TPZL ascii:", "".join(chr(c) if 32 <= c < 127 else "." for c in seg))
