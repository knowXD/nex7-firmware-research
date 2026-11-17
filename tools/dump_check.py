#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dump_check.py -- 拿到 NAND dump / 分区镜像后，先跑这个。

它做的事（全部只读，不改文件）：
  1. 判断几何：是不是 2048(+OOB) 页、总量像不像 128MiB 芯片
  2. 按已知分区偏移 + 全片扫描，找出所有 vfat 卷
  3. 认出哪个是 /setting（根目录里有没有 MODE 目录）
  4. 列出 /setting 里的文件，并把 dmode / env.txt 的内容读出来
  5. 报告 dmode 是否已经是合法值

用法：
  python dump_check.py --in dump.bin --oob 64
  python dump_check.py --in setting.img --oob 0
  python dump_check.py --selftest
"""
import argparse
import os
import struct
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import setting_patch as sp   # 复用 FAT12/16 实现

PAGE = 2048
SETTING_BASE = 0x420000
KNOWN = [
    (0x000000, "block0/loader"),
    (0x020000, "nflasha1(updater)"),
    (0x0420000, "nflasha2 /setting"),
    (0x006A0000, "nflasha3 /system"),
    (0x00FA0000, "nflasha4"),
    (0x015A0000, "nflasha5 /wbi"),
    (0x039A0000, "nflasha7 /tmp"),
    (0x052A0000, "nflasha8 /usr"),
]


def flat_view(data, oob):
    """把 (2048+oob) 交错的原始 dump 变成纯数据流；oob=0 直接返回。"""
    if oob == 0:
        return data
    stride = PAGE + oob
    npages = len(data) // stride
    out = bytearray(npages * PAGE)
    for i in range(npages):
        src = i * stride
        out[i * PAGE:(i + 1) * PAGE] = data[src:src + PAGE]
    return bytes(out)


def vfat_candidates(flat):
    """在数据流里找所有像 vfat 引导扇区的位置（按 512 对齐）。"""
    out = []
    n = len(flat)
    for off in range(0, n - 512, 512):
        if flat[off + 510] != 0x55 or flat[off + 511] != 0xAA:
            continue
        bps = struct.unpack_from("<H", flat, off + 11)[0]
        spc = flat[off + 13]
        if bps != 512 or spc == 0 or spc > 128:
            continue
        fstype = bytes(flat[off + 54:off + 62])
        if b"FAT" not in fstype:
            continue
        out.append((off, fstype.decode("latin1").strip()))
    return out


def describe_volume(flat, off):
    vol = flat[off:off + 0x280000] if off + 0x280000 <= len(flat) else flat[off:]
    try:
        f = sp.Fat(bytearray(vol))
    except Exception as e:
        return None, "解析失败: %r" % (e,)
    names = []
    for e in f.read_dir(None):
        raw = f.buf[e:e + 32]
        if raw[0] in (0x00, 0xE5) or raw[11] == 0x0F:
            continue
        nm = raw[0:8].rstrip(b" \x00").decode("latin1") + "." + raw[8:11].rstrip(b" \x00").decode("latin1")
        nm = nm.rstrip(".")
        cl = struct.unpack_from("<H", raw, 26)[0]
        sz = struct.unpack_from("<I", raw, 28)[0]
        isdir = bool(raw[11] & 0x10)
        names.append((nm, sz, isdir, cl))
    return (f, names), None


def read_file(f, name, dir_cluster=None):
    hit = f.lookup(name, dir_cluster)
    if not hit:
        return None
    off, _, cl, sz = hit
    if cl < 2 or sz == 0 or sz > 0x10000:
        return b""
    start = f.cluster_off(cl)
    return bytes(f.buf[start:start + sz])


def check(path, oob):
    data = open(path, "rb").read()
    print("文件: %s (%d B)" % (path, len(data)))
    stride = PAGE + oob
    if oob and len(data) % stride:
        print("  ⚠️ 大小不是 %d 的整数倍（余 %d）——OOB 可能不是 %d" % (stride, len(data) % stride, oob))
    if oob == 0 and len(data) % PAGE:
        print("  ⚠️ 大小不是 2048 的整数倍（余 %d）" % (len(data) % PAGE))
    pages = len(data) // stride if oob else len(data) // PAGE
    print("  页数 ≈ %d，块数(128KB) ≈ %d" % (pages, pages * PAGE // 0x20000))

    flat = flat_view(data, oob)
    cands = vfat_candidates(flat)
    print("\nvfat 候选: %d 个" % len(cands))
    setting = None
    full_chip = 100 * 1024 * 1024 <= len(flat) <= 200 * 1024 * 1024
    for off, fstype in cands[:12]:
        where = next((n for p, n in KNOWN if p == off), "") if full_chip else ""
        print("  0x%08X %-8s %s" % (off, fstype, where))
        info, err = describe_volume(flat, off)
        if err:
            print("        -> %s" % err)
            continue
        f, names = info
        has_mode = any(n.upper() == "MODE" and isdir for n, _, isdir, _ in names)
        print("        %d 个条目%s | FAT%d 簇%d" % (
            len(names), " | 含 MODE 目录 ✅" if has_mode else "",
            f.bits, f.cluster_bytes))
        if has_mode and setting is None:
            setting = (off, f, names)

    if not setting:
        print("\n❌ 没认出 /setting（找不到含 MODE 目录的 vfat 卷）")
        return 1

    off, f, names = setting
    print("\n== /setting (0x%08X) ==" % off)
    for nm, sz, isdir, _ in names:
        print("   %-16s %8d %s" % (nm, sz, "DIR" if isdir else ""))

    mode_dir = f.lookup(b"MODE")
    mcl = struct.unpack_from("<H", f.buf, mode_dir[0] + 26)[0] if mode_dir else None
    dmode = read_file(f, b"DMODE", mcl)
    env = read_file(f, b"ENV.TXT")
    print("\n== 关键文件 ==")
    if dmode is None:
        print("   dmode: 不存在（缺省即 mode 3）")
    else:
        ok = dmode[:1] == b"3"
        print("   dmode: %r  %s" % (dmode, "✅ 合法" if ok else "❌ 非法"))
    print("   env.txt: %r" % (env,))
    return 0


def selftest():
    ok = True
    def chk(c, m):
        nonlocal ok
        print(("  [OK]   " if c else "  [FAIL] ") + m)
        if not c: ok = False

    vol = sp.make_test_volume()
    # 1) 纯数据镜像：把 /setting 放在 0x420000
    total = SETTING_BASE + len(vol) + PAGE
    img = bytearray(total)
    img[SETTING_BASE:SETTING_BASE + len(vol)] = vol
    open("nex7/tmp/selftest_flat.img", "wb").write(img)
    print("== 自检 1：flat 镜像 ==")
    rc = check("nex7/tmp/selftest_flat.img", 0)
    chk(rc == 0, "识别出 /setting")

    # 2) 带 OOB：同样内容，按 2048+64 交错
    stride = PAGE + 64
    npages = len(img) // PAGE
    raw = bytearray(npages * stride)
    for i in range(npages):
        raw[i * stride:i * stride + PAGE] = img[i * PAGE:(i + 1) * PAGE]
        raw[i * stride + PAGE:i * stride + PAGE + 64] = b"\xff" * 64
    open("nex7/tmp/selftest_oob.bin", "wb").write(raw)
    print("\n== 自检 2：带 64B OOB ==")
    rc = check("nex7/tmp/selftest_oob.bin", 64)
    chk(rc == 0, "OOB=64 下也能识别")

    print("\nSELFTEST %s" % ("PASSED" if ok else "FAILED"))
    return 0 if ok else 1


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp")
    ap.add_argument("--oob", type=int, default=64)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    if not a.inp:
        ap.error("需要 --in 或 --selftest")
    return check(a.inp, a.oob)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
