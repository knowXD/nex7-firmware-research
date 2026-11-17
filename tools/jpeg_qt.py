import sys
sys.path.append("nex7/pylibs")
from PIL import Image
import os
for n in ["DSC00100","DSC00101","DSC00102","DSC00103","DSC00104"]:
    p = "E:/DCIM/110MSDCF/%s.JPG" % n
    if not os.path.exists(p):
        print(n, "missing"); continue
    im = Image.open(p)
    q = im.quantization
    luma = q.get(0); chroma = q.get(1) if 1 in q else None
    def avg(t): return round(sum(t)/len(t), 2) if t else None
    print(n, "size", os.path.getsize(p), "dim", im.size, "subsampling", im.layer if hasattr(im,'layer') else None)
    print("   luma avg %.2f max %d | chroma avg %s max %s" % (avg(luma), max(luma), avg(chroma), max(chroma) if chroma else None))
    print("   luma first8", list(luma[:8]))
