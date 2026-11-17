#!/usr/bin/env python3
"""Parameterised film-look LUT generator.

Examples:
  python film_lut.py out.cube --preset velvia
  python film_lut.py out.cube --contrast 1.1 --sat 1.2 --fade 0.03 \
      --shadow-tint 0,0.01,0.03 --highlight-tint 0.03,0.01,0
"""
import argparse
import numpy as np

PRESETS = {
    # name: contrast, saturation, fade, rolloff, shadow_tint, highlight_tint, temp, tint, mono
    "provia":        (1.06, 1.05, 0.005, 0.05, (0.000, 0.000, 0.005), (0.005, 0.003, 0.000), 0.00, 0.00, False),
    "velvia":        (1.18, 1.38, 0.000, 0.02, (0.000, 0.000, 0.012), (0.010, 0.004, -0.004), 0.00, 0.00, False),
    "classic-chrome":(1.10, 0.80, 0.035, 0.10, (0.000, 0.010, 0.020), (0.015, 0.008, -0.005), 0.01, 0.00, False),
    "acros":         (1.22, 0.00, 0.010, 0.06, (0.005, 0.005, 0.008), (0.005, 0.005, 0.005), 0.00, 0.00, True),
    "portra":        (0.95, 0.92, 0.025, 0.12, (0.010, 0.004, 0.000), (0.020, 0.012, 0.000), 0.015, 0.005, False),
    "neutral":       (1.00, 1.00, 0.000, 0.00, (0, 0, 0), (0, 0, 0), 0.00, 0.00, False),
}

def srgb_to_linear(x):
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)

def linear_to_srgb(x):
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(np.maximum(x, 0), 1 / 2.4) - 0.055)

def apply_look(rgb, contrast, sat, fade, rolloff, st, ht, temp, tint, mono):
    x = np.clip(rgb, 0.0, 1.0)
    # white balance shift (simple channel gains)
    x = x * np.array([1.0 + temp, 1.0 + tint, 1.0 - temp], dtype=np.float32)
    x = np.clip(x, 0.0, 1.0)
    # tone
    y = np.clip((x - 0.5) * contrast + 0.5, 0.0, 1.0)
    if fade > 0:
        y = fade + y * (1.0 - fade)
    if rolloff > 0:
        y = 1.0 - np.power(np.maximum(1.0 - y, 0.0), 1.0 + rolloff)
    # luminance
    luma = (0.2126 * y[..., 0] + 0.7152 * y[..., 1] + 0.0722 * y[..., 2])[..., None]
    if mono:
        y = np.repeat(luma, 3, axis=-1)
    else:
        y = luma + (y - luma) * sat
    # split toning
    s = np.array(st, dtype=np.float32); h = np.array(ht, dtype=np.float32)
    y = y + s * (1.0 - luma) + h * luma
    return np.clip(y, 0.0, 1.0)

def write_cube(path, fn, n=33):
    lines = ['TITLE "film"', "LUT_3D_SIZE %d" % n, "DOMAIN_MIN 0 0 0", "DOMAIN_MAX 1 1 1"]
    for b in range(n):
        for g in range(n):
            for r in range(n):
                rgb = np.array([r, g, b], dtype=np.float32) / (n - 1)
                o = fn(rgb)
                lines.append("%.6f %.6f %.6f" % (o[0], o[1], o[2]))
    open(path, "w").write("\n".join(lines) + "\n")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--preset", choices=list(PRESETS), default=None)
    ap.add_argument("--contrast", type=float); ap.add_argument("--sat", type=float)
    ap.add_argument("--fade", type=float); ap.add_argument("--rolloff", type=float)
    ap.add_argument("--shadow-tint"); ap.add_argument("--highlight-tint")
    ap.add_argument("--temp", type=float); ap.add_argument("--tint", type=float)
    ap.add_argument("--mono", action="store_true")
    ap.add_argument("--size", type=int, default=33)
    a = ap.parse_args()

    if a.preset:
        c, s, f, ro, st, ht, tp, tn, mono = PRESETS[a.preset]
    else:
        c = s = f = ro = tp = tn = 0.0
        c = 1.0; s = 1.0; ro = 0.0; f = 0.0; st = (0, 0, 0); ht = (0, 0, 0); mono = False
    c = a.contrast if a.contrast is not None else c
    s = a.sat if a.sat is not None else s
    f = a.fade if a.fade is not None else f
    ro = a.rolloff if a.rolloff is not None else ro
    tp = a.temp if a.temp is not None else tp
    tn = a.tint if a.tint is not None else tn
    mono = a.mono or mono
    if a.shadow_tint:
        st = tuple(float(x) for x in a.shadow_tint.split(","))
    if a.highlight_tint:
        ht = tuple(float(x) for x in a.highlight_tint.split(","))

    fn = lambda rgb: apply_look(rgb, c, s, f, ro, st, ht, tp, tn, mono)
    write_cube(a.out, fn, a.size)
    print("wrote", a.out, "(contrast %.2f sat %.2f fade %.3f rolloff %.2f)" % (c, s, f, ro))

if __name__ == "__main__":
    main()
