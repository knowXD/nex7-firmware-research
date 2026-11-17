import re
tr = open("session-handoff/B-nex7-transcript.md", "r", encoding="utf-8").read().replace("\r\n", "\n")
lines = tr.split("\n")
turn_re = re.compile(r"^## Turn (\d+) · (用户|助手|工具结果)?\s*·?\s*([0-9T:.\- ]*)")
cur = ("?", "?")
out = []
for ln in lines:
    m = turn_re.match(ln)
    if m:
        cur = (m.group(1), m.group(3).strip()[:19])
    if re.search(r"Mbps", ln) and ("size" in ln or "bitrate" in ln.lower() or "0004" in ln):
        s = ln.strip()
        if len(s) < 400:
            out.append((cur[0], cur[1], s))
print("== Mbps 测量记录 ==")
for t, ts, s in out:
    print("  T%-4s %-20s %s" % (t, ts, s[:150]))
