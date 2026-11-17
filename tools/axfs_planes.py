d = open("nex7/work_initrd.img","rb").read()
off, n = 0x7EC, 1136
planes = [d[off+i*n:off+(i+1)*n] for i in range(4)]
for i, p in enumerate(planes):
    print("plane", i, "zero%", round(100*p.count(0)/len(p),1), "max", max(p))
# combine
vals = [planes[0][j] | (planes[1][j]<<8) | (planes[2][j]<<16) | (planes[3][j]<<24) for j in range(n)]
print("first 12 values", vals[:12], "max", max(vals))
