from PIL import Image
im = Image.open(r"C:/Users/<user>/.dsh/attachments/v1/objects/33/3313458c8ffa699d62d65c09269162e4a7968e1afd690df8371a0b9070cae1de")
print(im.size)
# crop center-bottom chip area
w,h = im.size
box = (int(w*0.36), int(h*0.55), int(w*0.62), int(h*0.90))
c = im.crop(box)
c = c.resize((c.width*4, c.height*4), Image.LANCZOS)
c.save("nex7/dl/teardown/chip_zoom.png")
print("saved", c.size)
