import os, glob
from PIL import Image
rows = []
for p in glob.glob("E:/DCIM/*/*.JPG"):
    try:
        im = Image.open(p)
        q = im.quantization
        luma = q.get(0)
        avg = sum(luma)/len(luma)
        rows.append((os.path.basename(p), os.path.getsize(p), round(avg,2), len(luma)))
    except Exception as e:
        rows.append((os.path.basename(p), os.path.getsize(p), "ERR", 0))
rows.sort(key=lambda r: r[0])
for r in rows[-40:]:
    print(r)
print("total", len(rows))
