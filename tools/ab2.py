import os, glob
from PIL import Image
for folder, label in [("111MSDCF","prev patched STD"),("112MSDCF","prev patched FINE"),("113MSDCF","stock STD"),("114MSDCF","stock FINE"),("115MSDCF","new all-table STD"),("116MSDCF","new all-table FINE")]:
    files = sorted(glob.glob("E:/DCIM/%s/*.JPG" % folder))
    if not files:
        print(folder, label, "none"); continue
    p = files[-1]
    im = Image.open(p)
    q = im.quantization
    print("%-8s %-20s %-14s size=%-8d luma=%.2f chroma=%.2f first8=%s" % (
        folder, label, os.path.basename(p), os.path.getsize(p),
        sum(q[0])/64, sum(q[1])/64, list(q[0][:8])))
