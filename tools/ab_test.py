import os, glob
from PIL import Image
for folder, label in [("111MSDCF","补丁 STD"),("112MSDCF","补丁 FINE"),("113MSDCF","原厂 STD"),("114MSDCF","原厂 FINE")]:
    files = sorted(glob.glob("E:/DCIM/%s/*.JPG" % folder))
    if not files:
        print(folder, label, "no files"); continue
    for p in files[-2:]:
        im = Image.open(p)
        q = im.quantization
        luma = q.get(0); chroma = q.get(1)
        print("%-12s %-8s %s size=%-8d luma_avg=%.2f chroma_avg=%.2f first8=%s layer=%s" % (
            folder, label, os.path.basename(p), os.path.getsize(p),
            sum(luma)/64, sum(chroma)/64, list(luma[:8]), im.layer))
