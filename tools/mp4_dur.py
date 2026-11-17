import struct, os
p = "E:/MP_ROOT/118ANV01/MAH00114.MP4"
d = open(p,"rb").read()
def find_box(buf, name, start=0):
    i = start
    while i + 8 <= len(buf):
        size = struct.unpack_from(">I", buf, i)[0]
        typ = buf[i+4:i+8]
        if size == 0: break
        if typ == name: return i, size
        i += size if size >= 8 else 8
    return None, None
def walk(buf, base=0):
    i = 0
    while i + 8 <= len(buf):
        size = struct.unpack_from(">I", buf, i)[0]
        typ = buf[i+4:i+8]
        if size < 8: break
        if typ in (b"mvhd", b"mdhd"):
            ver = buf[i+8]
            if ver == 0:
                ts, dur = struct.unpack_from(">II", buf, i+8+4+4+4)
                print(typ, "timescale", ts, "duration", dur, "sec", dur/ts if ts else 0)
            else:
                ts, dur = struct.unpack_from(">IQ", buf, i+8+4+8+8)
                print(typ, "timescale", ts, "duration", dur, "sec", dur/ts if ts else 0)
        if typ in (b"moov", b"trak", b"mdia"):
            walk(buf[i+8:i+size])
        i += size
walk(d)
print("size", os.path.getsize(p))
