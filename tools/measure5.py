import os
def mts_dur(path):
    d = open(path,'rb').read()
    psize, off = 192, 4
    if len(d) < 200 or d[4] != 0x47:
        psize, off = 188, 0
    first = last = None
    for i in range(0, len(d)-psize, psize):
        q = d[i+off:i+off+188]
        if q[0] != 0x47: continue
        af = (q[3] >> 4) & 0x3
        if af in (2,3):
            afl = q[4]
            if afl > 0 and (q[5] & 0x10):
                base = ((q[6]<<25)|(q[7]<<17)|(q[8]<<9)|(q[9]<<1)|(q[10]>>7))
                if first is None: first = base
                last = base
    return (last-first)/90000.0 if first is not None else 0
for n in ["00052","00053"]:
    p = "E:/PRIVATE/AVCHD/BDMV/STREAM/%s.MTS" % n
    dur = mts_dur(p)
    print(n, "size", os.path.getsize(p), "dur %.2f" % dur, "bitrate %.2f Mbps" % (os.path.getsize(p)*8/dur/1e6))
