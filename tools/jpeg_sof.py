import os, struct
from PIL import Image
def sof0(p):
    d = open(p,"rb").read()
    i = 2
    while i < len(d)-4:
        if d[i] != 0xFF:
            i += 1; continue
        m = d[i+1]
        if m in (0xC0,0xC1,0xC2):
            ln = struct.unpack_from(">H", d, i+2)[0]
            prec = d[i+4]; h = struct.unpack_from(">H", d, i+5)[0]; w = struct.unpack_from(">H", d, i+7)[0]
            nc = d[i+9]
            comps = []
            for k in range(nc):
                cid = d[i+10+3*k]; hv = d[i+11+3*k]; tq = d[i+12+3*k]
                comps.append((cid, hv>>4, hv&0xf, tq))
            return (m, w, h, comps)
        if m in (0xD8,0xD9) or 0xD0 <= m <= 0xD7:
            i += 2; continue
        ln = struct.unpack_from(">H", d, i+2)[0]
        i += 2 + ln
    return None
for n in ["DSC00100","DSC00103","DSC00104"]:
    p = "E:/DCIM/110MSDCF/%s.JPG" % n
    if not os.path.exists(p): continue
    im = Image.open(p)
    ex = im._getexif() if hasattr(im,"_getexif") else {}
    dt = ex.get(36867) if ex else None
    print(n, "size", os.path.getsize(p), "datetime", dt, "sof", sof0(p))
