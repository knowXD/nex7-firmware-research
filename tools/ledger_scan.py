import re, os, glob, json

tr = open("session-handoff/B-nex7-transcript.md", "r", encoding="utf-8").read().replace("\r\n", "\n")
lines = tr.split("\n")

# 1) 构建：找含 fw_build.py 的行，提取 --out 与 --replace-member
builds = {}
for ln in lines:
    if "fw_build.py" not in ln: continue
    m = re.search(r"--out\s+(nex7/[A-Za-z0-9_./-]+\.tar)", ln)
    if not m: continue
    tarname = m.group(1)
    reps = re.findall(r"0700_part_image/dev/(nflasha\d)=nex7/([A-Za-z0-9_.]+)", ln)
    build = (tarname, reps)
    # pack 目标
    for pk in re.findall(r"-o\s+(nex7/out_[A-Za-z0-9_]+)", ln):
        builds.setdefault(pk.replace("nex7/", ""), []).append(build)

# 2) 刷写：找 firmware 命令 + 重定向日志
flashes = {}
for ln in lines:
    m = re.search(r"firmware[^\n\"]*-f\s+\"?[^\"]*?(out_[A-Za-z0-9_]+)/firmware_packed\.dat\",?\s*\*\>\s*([^\"\s]+\.log)", ln)
    if m:
        pkg, log = m.group(1), os.path.basename(m.group(2))
        flashes.setdefault(pkg, []).append(log)

print("== 构建记录（包 -> tar + 替换成员）==")
for k, v in sorted(builds.items()):
    for tarname, reps in v:
        print("  %-18s <- %-22s %s" % (k, os.path.basename(tarname), reps))

print("\n== 刷写记录（包 -> 日志）==")
seen = set()
for k, v in sorted(flashes.items()):
    for log in v:
        if (k, log) in seen: continue
        seen.add((k, log))
        p = os.path.join("nex7", log)
        status = "MISSING"
        if os.path.exists(p):
            t = open(p, "rb").read().decode("latin1", "replace").replace("\x00", "")
            status = "OK" if ("100%" in t and "Done" in t) else ("NO_DEVICE" if "No devices found" in t else "ERR")
        print("  %-18s -> %-26s %s" % (k, log, status))

print("\n== 未被任何刷卡引用的 out_* ==")
for d in sorted(glob.glob("nex7/out_*")):
    name = os.path.basename(d)
    if name not in flashes:
        print("  ", name)
