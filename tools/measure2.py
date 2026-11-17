import struct, os
# MP4
p = "E:/MP_ROOT/118ANV01/MAH00116.MP4"
d = open(p,"rb").read()
def walk(buf):
    i = 0
    while i + 8 <= len(buf):
        size = struct.unpack_from(">I", buf, i)[0]
        typ = buf[i+4:i+8]
        if size < 8: break
        if typ == b"mvhd":
            ver = buf[i+8]
            if ver == 0:
                ts, dur = struct.unpack_from(">II", buf, i+8+4+4+4)
                print("MP4 timescale", ts, "duration", dur, "sec %.2f" % (dur/ts))
                print("MP4 size", os.path.getsize(p), "bitrate %.2f Mbps" % (os.path.getsize(p)*8/(dur/ts)/1e6))
        if typ in (b"moov",):
            walk(buf[i+8:i+size])
        i += size
walk(d)
# MTS
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
p2 = "E:/PRIVATE/AVCHD/BDMV/STREAM/00048.MTS"
dur = mts_dur(p2)
print("MTS size", os.path.getsize(p2), "dur %.2f" % dur, "bitrate %.2f Mbps" % (os.path.getsize(p2)*8/dur/1e6))
