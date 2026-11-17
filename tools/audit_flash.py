import os, re, glob, hashlib

print("### flash_*.log 行为审计 ###")
rows = []
for f in sorted(glob.glob("nex7/flash*.log")):
    t = open(f, "rb").read().decode("latin1", "replace").replace("\x00", "")
    ok = "100%" in t and "Done" in t
    nodev = "No devices found" in t
    err = "Traceback" in t or "EXIT=1" in t
    ver = ""
    m = re.search(r"Updating from version ([\d.]+) to version ([\d.]+)", t)
    if m: ver = "%s->%s" % m.groups()
    rows.append((os.path.basename(f), os.path.getsize(f),
                 "OK" if ok else ("NO_DEVICE" if nodev else ("ERR" if err else "?")), ver))
for r in rows:
    print("   %-28s %6d  %-10s %s" % r)
print("\n成功 %d / 无设备 %d / 报错 %d / 不明 %d" % (
    sum(1 for r in rows if r[2]=="OK"), sum(1 for r in rows if r[2]=="NO_DEVICE"),
    sum(1 for r in rows if r[2]=="ERR"), sum(1 for r in rows if r[2]=="?")))

print("\n### out_* 包（mtime 与大小） ###")
for d in sorted(glob.glob("nex7/out_*")):
    p = os.path.join(d, "firmware_packed.dat")
    if os.path.exists(p):
        st = os.stat(p)
        import datetime
        print("   %-22s %10d  %s" % (os.path.basename(d), st.st_size,
              datetime.datetime.fromtimestamp(st.st_mtime).strftime("%m-%d %H:%M")))

print("\n### 测量相关脚本/日志 ###")
for f in sorted(glob.glob("nex7/*measure*") + glob.glob("nex7/*bitrate*") + glob.glob("nex7/mts*.log")):
    print("   %-32s %7d" % (os.path.basename(f), os.path.getsize(f)))
