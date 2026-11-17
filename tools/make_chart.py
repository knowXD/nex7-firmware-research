import numpy as np
from PIL import Image
h,w=256,384
img=np.zeros((h,w,3),np.uint8)
for y in range(h):
    for x in range(w):
        img[y,x]=[int(255*x/(w-1)), int(255*y/(h-1)), 128]
patches=[(255,0,0),(0,255,0),(0,0,255),(255,255,0),(0,255,255),(255,0,255),(128,128,128),(200,180,150)]
for i,(r,g,b) in enumerate(patches):
    x0=10+(i%4)*90; y0=10+(i//4)*60
    img[y0:y0+50,x0:x0+80]=[r,g,b]
Image.fromarray(img).save("nex7/hack/test_chart.png")
print("chart saved")
