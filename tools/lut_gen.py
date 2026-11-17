#!/usr/bin/env python3
"""Generate test .cube LUTs (identity / warm film look)."""
import numpy as np, sys

def write_cube(path, fn, n=33):
    lines = ["TITLE \"test\"", "LUT_3D_SIZE %d" % n, "DOMAIN_MIN 0 0 0", "DOMAIN_MAX 1 1 1"]
    for b in range(n):
        for g in range(n):
            for r in range(n):
                rgb = np.array([r, g, b], dtype=np.float32) / (n - 1)
                o = fn(rgb)
                lines.append("%.6f %.6f %.6f" % (o[0], o[1], o[2]))
    open(path, "w").write("\n".join(lines) + "\n")

def identity(c):
    return c

def warm(c):
    # gentle S-curve + warm shift + slight fade
    x = np.clip(c, 0, 1)
    s = x * x * (3 - 2 * x)
    out = 0.15 * x + 0.85 * s
    out = out * np.array([1.03, 1.00, 0.95]) + np.array([0.01, 0.005, 0.0])
    return np.clip(out, 0, 1)

if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "identity"
    out = sys.argv[2] if len(sys.argv) > 2 else which + ".cube"
    write_cube(out, identity if which == "identity" else warm)
    print("wrote", out)
