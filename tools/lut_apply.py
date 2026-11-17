#!/usr/bin/env python3
"""Apply a .cube 3D LUT to images (PC prototype for in-camera film looks).

Usage:
  python lut_apply.py input.jpg output.jpg look.cube [--quality 95]
  python lut_apply.py indir outdir look.cube
"""
import sys, os, argparse
import numpy as np
from PIL import Image

def read_cube(path):
    size = None
    data = []
    dmin = np.array([0.0, 0.0, 0.0])
    dmax = np.array([1.0, 1.0, 1.0])
    for line in open(path, "r", errors="ignore"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if line.upper().startswith("LUT_3D_SIZE"):
            size = int(line.split()[-1])
        elif line.upper().startswith("DOMAIN_MIN"):
            dmin = np.array([float(x) for x in line.split()[1:4]])
        elif line.upper().startswith("DOMAIN_MAX"):
            dmax = np.array([float(x) for x in line.split()[1:4]])
        elif line.upper().startswith(("TITLE", "LUT_1D_SIZE")):
            continue
        else:
            parts = line.split()
            if len(parts) == 3:
                data.append([float(x) for x in parts])
    if size is None:
        raise ValueError("no LUT_3D_SIZE")
    arr = np.array(data, dtype=np.float32)
    if arr.shape[0] != size ** 3:
        raise ValueError("expected %d entries, got %d" % (size ** 3, arr.shape[0]))
    # .cube: red changes fastest -> reshape (b, g, r, 3)
    lut = arr.reshape(size, size, size, 3)
    return lut, dmin, dmax

def apply_lut(img, lut, dmin, dmax):
    # img: float32 HxWx3 in 0..1 (sRGB)
    n = lut.shape[0]
    v = np.clip((img - dmin) / (dmax - dmin + 1e-9), 0.0, 1.0)
    x = v[..., 0] * (n - 1)
    y = v[..., 1] * (n - 1)
    z = v[..., 2] * (n - 1)
    x0 = np.floor(x).astype(np.int32); y0 = np.floor(y).astype(np.int32); z0 = np.floor(z).astype(np.int32)
    x1 = np.minimum(x0 + 1, n - 1); y1 = np.minimum(y0 + 1, n - 1); z1 = np.minimum(z0 + 1, n - 1)
    fx = (x - x0)[..., None]; fy = (y - y0)[..., None]; fz = (z - z0)[..., None]

    def c(zi, yi, xi):
        return lut[zi, yi, xi]

    c000 = c(z0, y0, x0); c100 = c(z0, y0, x1)
    c010 = c(z0, y1, x0); c110 = c(z0, y1, x1)
    c001 = c(z1, y0, x0); c101 = c(z1, y0, x1)
    c011 = c(z1, y1, x0); c111 = c(z1, y1, x1)

    c00 = c000 * (1 - fx) + c100 * fx
    c01 = c010 * (1 - fx) + c110 * fx
    c10 = c001 * (1 - fx) + c101 * fx
    c11 = c011 * (1 - fx) + c111 * fx
    c0 = c00 * (1 - fy) + c01 * fy
    c1 = c10 * (1 - fy) + c11 * fy
    out = c0 * (1 - fz) + c1 * fz
    return np.clip(out, 0.0, 1.0)

def process(src, dst, lut, dmin, dmax, quality, grain=0.0):
    im = Image.open(src).convert("RGB")
    arr = np.asarray(im).astype(np.float32) / 255.0
    out = apply_lut(arr, lut, dmin, dmax)
    if grain > 0:
        noise = np.random.normal(0.0, grain, out.shape).astype(np.float32)
        out = np.clip(out + noise, 0.0, 1.0)
    Image.fromarray((out * 255.0 + 0.5).astype(np.uint8)).save(dst, quality=quality, subsampling=0)
    print("wrote", dst)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src"); ap.add_argument("dst"); ap.add_argument("cube")
    ap.add_argument("--quality", type=int, default=95)
    ap.add_argument("--grain", type=float, default=0.0)
    a = ap.parse_args()
    lut, dmin, dmax = read_cube(a.cube)
    print("LUT size", lut.shape[0])
    if os.path.isdir(a.src):
        os.makedirs(a.dst, exist_ok=True)
        for f in sorted(os.listdir(a.src)):
            if f.lower().endswith((".jpg", ".jpeg", ".png")):
                process(os.path.join(a.src, f), os.path.join(a.dst, f), lut, dmin, dmax, a.quality, a.grain)
    else:
        process(a.src, a.dst, lut, dmin, dmax, a.quality, a.grain)

if __name__ == "__main__":
    main()
