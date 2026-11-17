import os, glob
from PIL import Image
im = Image.open("E:/DCIM/115MSDCF/DSC00110.JPG")
q = im.quantization[0]
print("DQT luma 64 bytes:", list(q))
open("nex7/hack/std_dqt.bin","wb").write(bytes(q))
im2 = Image.open("E:/DCIM/116MSDCF/DSC00111.JPG")
q2 = im2.quantization[0]
open("nex7/hack/fine_dqt.bin","wb").write(bytes(q2))
print("DQT fine 64 bytes:", list(q2))
