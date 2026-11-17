import sys
base, stub, out = sys.argv[1], sys.argv[2], sys.argv[3]
OFF, LEN = 0xD1C400, 11516
d = bytearray(open(base, "rb").read())
s = open(stub, "rb").read()
if len(s) != LEN:
    sys.exit("stub size %d != %d" % (len(s), LEN))
d[OFF:OFF+LEN] = s
open(out, "wb").write(d)
print("patched %s -> %s at 0x%X (%d bytes)" % (base, out, OFF, len(d)))
