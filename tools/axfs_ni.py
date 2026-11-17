from collections import Counter
d = open("nex7/work_initrd.img","rb").read()
blob = d[0x7EC:0x7EC+4544]
c = Counter(blob)
print("node_index region distinct", len(c), "max", max(blob), "min", min(blob))
print("top", c.most_common(8))
# check if it's a monotonic byte stream
mono = all(blob[i] <= blob[i+1] for i in range(len(blob)-1))
print("monotonic bytes?", mono)
# try BE16 stats
vals16 = [ (blob[i]<<8)|blob[i+1] for i in range(0,len(blob)-1,2)]
print("first 12 u16", vals16[:12], "max", max(vals16))
# try BE32 stats
vals32 = [ (blob[i]<<24)|(blob[i+1]<<16)|(blob[i+2]<<8)|blob[i+3] for i in range(0,len(blob)-3,4)]
print("first 8 u32", vals32[:8], "max", max(vals32), "small(<2000)", sum(1 for v in vals32 if v<2000))
