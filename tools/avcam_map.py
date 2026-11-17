import re
from collections import Counter
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p, "rb").read()
strs = [(m.start(), m.group().decode("latin1")) for m in re.finditer(rb"[\x20-\x7e]{8,}", d)]
print("strings", len(strs))
# cluster: gap > 32KB starts a new cluster
clusters = []
cur = []
for off, s in strs:
    if cur and off - cur[-1][0] > 32768:
        clusters.append(cur); cur = []
    cur.append((off, s))
if cur: clusters.append(cur)
print("clusters", len(clusters))
big = [c for c in clusters if len(c) >= 40]
print("big clusters", len(big))
for c in sorted(big, key=lambda x: -len(x))[:20]:
    start, end = c[0][0], c[-1][0]
    # notable tokens: words with uppercase/module-ish
    words = Counter()
    for _, s in c:
        for w in re.findall(r"[A-Za-z_][A-Za-z0-9_]{3,}", s):
            if any(k in w for k in ("Codec","Jpeg","JPEG","Dgi","DGI","Vdf","VDF","Isp","ISP","Enc","Dec","Cam","Movie","Still","Audio","Exif","Scene","Color","Gamma","Lut","LUT","Tone","Zebra","Focus","Ae","Awb")):
                words[w] += 1
    top = ", ".join(w for w, _ in words.most_common(6))
    print(hex(start), "-", hex(end), "strings", len(c), "|", top[:120])
