import os
from PIL import Image
for n in ["DSC06659","DSC06700"]:
    p = "E:/DCIM/" + ("100MSDCF/" if os.path.exists("E:/DCIM/100MSDCF/%s.JPG"%n) else "") + n + ".JPG"
    if not os.path.exists(p):
        import glob
        g = glob.glob("E:/DCIM/*/%s.JPG" % n)
        p = g[0] if g else None
    if not p: print(n,"missing"); continue
    im = Image.open(p)
    print(n, os.path.getsize(p), im.layer, im.quantization[0][:8], round(sum(im.quantization[0])/64,2))
