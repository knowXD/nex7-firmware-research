import re
from collections import defaultdict
p = "nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha3_unpacked_unpacked/av-cam.bin"
d = open(p, "rb").read()
seen = {}
for m in re.finditer(rb"[A-Za-z0-9_./\\-]+\.(?:cpp|cxx|cc|c|hpp|h)\x00", d):
    s = m.group()[:-1].decode("latin1")
    if s not in seen:
        seen[s] = m.start()
groups = defaultdict(list)
def classify(s):
    low = s.lower()
    if "dgi_jpeg" in low or "jpeg" in low: return "JPEG 编解码"
    if low.startswith("src/rc") or "/rc" in low: return "Resize/Copy"
    if low.startswith("tskavc") or "avcenc" in low or "avcdec" in low: return "AVC 编解码"
    if low.startswith("cdcmgr"): return "编码控制状态机"
    if low.startswith("mc"): return "Media Core"
    if low.startswith("fc/"): return "对焦控制"
    if low.startswith("sync/"): return "同步/时钟"
    if low.startswith("capture") or "capcon" in low or low.startswith("tsk_rawdev"): return "拍摄流程"
    if low.startswith("tsk_sdf"): return "SDF 任务"
    if low.startswith("subsystem"): return "子系统框架"
    if low.startswith("sdf"): return "SDF 调试"
    if low.startswith("stage_"): return "Stage"
    if low.startswith("function/"): return "Function 层"
    if low.startswith("imaging"): return "Imaging"
    if low.startswith("exif") or "exif" in low: return "EXIF"
    return "其他"
for s, off in seen.items():
    groups[classify(s)].append((off, s))
for g, items in sorted(groups.items(), key=lambda x: -len(x[1])):
    offs = sorted(o for o, _ in items)
    print("%-18s %3d 个  0x%06x - 0x%06x" % (g, len(items), offs[0], offs[-1]))
