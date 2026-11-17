import os
def duration(path):
    d = open(path,'rb').read()
    psize, off = 192, 4
    if len(d) < 200 or d[4] != 0x47:
        psize, off = 188, 0
    first = last = None
    for i in range(0, len(d)-psize, psize):
        p = d[i+off:i+off+188]
        if p[0] != 0x47: continue
        af = (p[3] >> 4) & 0x3
        if af in (2,3):
            afl = p[4]
            if afl > 0 and (p[5] & 0x10):
                base = ((p[6]<<25)|(p[7]<<17)|(p[8]<<9)|(p[9]<<1)|(p[10]>>7))
                if first is None: first = base
                last = base
    if first is None: return None
    return (last - first)/90000.0

for n, label in [("00043","PS 50p"), ("00044","FX mode1"), ("00045","FX mode2")]:
    p = "E:/PRIVATE/AVCHD/BDMV/STREAM/%s.MTS" % n
    dur = duration(p)
    size = os.path.getsize(p)
    mbps = size*8/dur/1e6 if dur else None
    print(n, label, "size", size, "dur %.2f" % (dur or 0), "bitrate %.2f Mbps" % (mbps or 0))
