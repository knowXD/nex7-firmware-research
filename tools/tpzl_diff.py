#!/usr/bin/env python3
"""Structural diff of two TPZL images: catches segmentation/format deviations."""
import sys, struct, io, os
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "fwtool.py-master"))
from fwtool.lz77 import inflateLz77

def parse(path):
    d = open(path, "rb").read()
    magic, bs, tocoff, tocsz = struct.unpack_from("<4sIII", d, 0)
    n = tocsz // 8
    blocks = []
    for i in range(n):
        off, size = struct.unpack_from("<II", d, tocoff + i * 8)
        raw = d[off:off + size]
        b = io.BytesIO(raw)
        read = 0; chunks = []; stores = 0
        while read < (1 << bs):
            first = raw[b.tell():b.tell()+1]
            if first == b"\x0f":
                stores += 1
            c = inflateLz77(b)
            chunks.append(len(c)); read += len(c)
            if len(chunks) > 256:
                break
        blocks.append((chunks, stores))
    return dict(magic=magic, blockSize=bs, tocoff=tocoff, tocsz=tocsz, n=n, blocks=blocks, size=len(d))

def main(newp, refp):
    a = parse(newp); b = parse(refp)
    print("new:", os.path.basename(newp), "size", a["size"])
    print("ref:", os.path.basename(refp), "size", b["size"])
    ok = True
    for k in ("magic", "blockSize", "tocoff", "tocsz", "n"):
        if a[k] != b[k]:
            ok = False
            print("  HEADER MISMATCH %s: %r vs %r" % (k, a[k], b[k]))
    if a["n"] != b["n"]:
        print("  block count mismatch"); return 1
    bad = 0
    for i in range(a["n"]):
        ca, sa = a["blocks"][i]; cb, sb = b["blocks"][i]
        if ca != cb or sa != sb:
            bad += 1
            if bad <= 5:
                print("  block %d: new chunks %s (store %d) vs ref chunks %s (store %d)" % (i, ca[:4], sa, cb[:4], sb))
    print("  blocks with chunk structure mismatch:", bad, "/", a["n"])
    return 0 if (ok and bad == 0) else 1

if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2]))
