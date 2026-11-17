#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""setting_patch.py -- 在有 NAND dump 的前提下，修好 /setting/mode/dmode。

背景：NEX-7 变砖是因为 /setting/mode/dmode 里写的是 'x'（0x78），
init 解析不出 '3' 前缀就不启动 sen.elf。本脚本只做三处最小改动：

  1. /mode/dmode   内容改回 "3\n"（2 字节），目录项长度 1 -> 2
  2. /env.txt      删除（目录项首字节 0xE5 + 释放簇链）
  3. /ldtest.so    删除（同上）

其它字节一个都不动，所以逐机校准数据（DmmConfig.bin 等）原样保留。

两种 dump 格式都支持：
  --oob 0    纯数据镜像（每页只有 2048 字节数据）
  --oob 64   编程器原始读取格式（2048 数据 + 64 备用区，交错排列）

用法：
  python setting_patch.py --in dump.bin --out dump_fixed.bin [--oob 64] [--report report.txt]
  python setting_patch.py --selftest          # 自检：造一个和真相机同构的 vfat 镜像测一遍
"""

import argparse
import os
import struct
import sys

PAGE = 2048
BLOCK = 0x20000          # 128KB 擦除块
SETTING_BASE = 0x420000  # /setting 在 NAND 上的起点（partinf.conf）
SETTING_SIZE = 0x280000  # 2.5MB

DMODE_TARGET = {b"DMODE": b"3\n"}   # 要写回的内容
DELETE_NAMES = [b"ENV.TXT", b"LDTEST.SO"]


# --------------------------------------------------------------------------
# 小工具
# --------------------------------------------------------------------------
def u16(b, off):
    return b[off] | (b[off + 1] << 8)


def u32(b, off):
    return b[off] | (b[off + 1] << 8) | (b[off + 2] << 16) | (b[off + 3] << 24)


class Dump:
    """把「逻辑偏移」和「物理偏移」互相转换。oob=0 时两者相同。"""

    STRIDE = PAGE  # 会在 __init__ 里改

    def __init__(self, data, oob, base):
        self.data = bytearray(data)
        self.oob = oob
        self.stride = PAGE + oob
        self.base = base

    def phys(self, logical):
        if self.oob == 0:
            return logical
        page, off = divmod(logical, PAGE)
        return page * self.stride + off

    def read_flat(self, off, size):
        if self.oob == 0:
            return bytes(self.data[off:off + size])
        out = bytearray(size)
        start = off
        end = off + size
        pos = 0
        while start < end:
            page, bo = divmod(start, PAGE)
            n = min(PAGE - bo, end - start)
            src = page * self.stride + bo
            out[pos:pos + n] = self.data[src:src + n]
            start += n
            pos += n
        return bytes(out)

    def write_flat(self, off, buf):
        if self.oob == 0:
            self.data[off:off + len(buf)] = buf
            return
        start = off
        end = off + len(buf)
        pos = 0
        while start < end:
            page, bo = divmod(start, PAGE)
            n = min(PAGE - bo, end - start)
            dst = page * self.stride + bo
            self.data[dst:dst + n] = buf[pos:pos + n]
            start += n
            pos += n


# --------------------------------------------------------------------------
# FAT12/16 最小实现（够用就好）
# --------------------------------------------------------------------------
class Fat:
    def __init__(self, buf):
        self.buf = buf
        self.bps = u16(buf, 11)
        self.spc = buf[13]
        self.rsvd = u16(buf, 14)
        self.nfats = buf[16]
        self.root_ents = u16(buf, 17)
        tot16 = u16(buf, 19)
        fatsz = u16(buf, 22)
        if tot16:
            total = tot16
        else:
            total = u32(buf, 32)
            if fatsz == 0:
                fatsz = u32(buf, 36)
        if self.bps != 512:
            raise ValueError("bytes/sector = %d，不是 512，拒绝处理" % self.bps)
        if self.spc == 0:
            raise ValueError("sectors/cluster = 0")
        self.fatsz = fatsz
        self.total_bytes = total * self.bps
        self.root_off = (self.rsvd + self.nfats * fatsz) * self.bps
        self.root_size = self.root_ents * 32
        self.data_off = self.root_off + self.root_size
        self.cluster_bytes = self.spc * self.bps
        nclusters = (self.total_bytes - self.data_off) // self.cluster_bytes
        self.count = nclusters + 2
        if self.count < 4085:
            self.bits = 12
        elif self.count < 65525:
            self.bits = 16
        else:
            raise ValueError("这是 FAT32 卷，本脚本不处理")

    # --- FAT 表 ---
    def fat_off(self, n, copy=0):
        base = (self.rsvd + copy * self.fatsz) * self.bps
        if self.bits == 12:
            return base + n + (n >> 1)
        return base + n * 2

    def fat_get(self, n):
        off = self.fat_off(n)
        if self.bits == 12:
            v = self.buf[off] | (self.buf[off + 1] << 8)
            return (v >> 4) if (n & 1) else (v & 0x0FFF)
        return u16(self.buf, off)

    def fat_set(self, n, val):
        for copy in range(self.nfats):
            off = self.fat_off(n, copy)
            if self.bits == 12:
                v = self.buf[off] | (self.buf[off + 1] << 8)
                if n & 1:
                    v = (v & 0x000F) | ((val & 0x0FFF) << 4)
                else:
                    v = (v & 0xF000) | (val & 0x0FFF)
                self.buf[off] = v & 0xFF
                self.buf[off + 1] = (v >> 8) & 0xFF
            else:
                self.buf[off] = val & 0xFF
                self.buf[off + 1] = (val >> 8) & 0xFF

    def eoc(self):
        return 0x0FFF if self.bits == 12 else 0xFFFF

    def chain(self, first):
        out, seen = [], set()
        c = first
        while 2 <= c < self.eoc() and c not in seen and len(out) < 200000:
            out.append(c)
            seen.add(c)
            c = self.fat_get(c)
        return out

    def free(self, first):
        n = 0
        for c in self.chain(first):
            self.fat_set(c, 0)
            n += 1
        return n

    def cluster_off(self, c):
        return self.data_off + (c - 2) * self.cluster_bytes

    # --- 目录 ---
    def read_dir(self, first_cluster=None):
        """返回目录项偏移列表；first_cluster 为 None 时读根目录。"""
        if not first_cluster:
            regions = [(self.root_off, self.root_size)]
        else:
            regions = [(self.cluster_off(c), self.cluster_bytes) for c in self.chain(first_cluster)]
        out = []
        for start, n in regions:
            pos = 0
            while pos + 32 <= n:
                off = start + pos
                if off + 32 > len(self.buf):
                    break
                if self.buf[off] == 0x00:
                    return out
                out.append(off)
                pos += 32
        return out

    def lookup(self, name, dir_cluster=None):
        """返回 (entry_offset, lfn_entry_offsets, cluster, size)；找不到返回 None。"""
        want = name.upper()
        lfn = []
        for off in self.read_dir(dir_cluster):
            raw = self.buf[off:off + 32]
            attr = raw[11]
            if attr == 0x0F:
                lfn.append((off, self.lfn_name(raw)))
                continue
            if raw[0] == 0xE5:
                lfn = []
                continue
            short = raw[0:8].rstrip(b" \x00").upper() + b"." + raw[8:11].rstrip(b" \x00").upper()
            if short.endswith(b"."):
                short = short[:-1]
            long_name = b"".join(x for _, x in reversed(lfn)) if lfn else None
            hit = (short == want) or (long_name is not None and long_name.upper() == want)
            if hit:
                cl = u16(raw, 26) | (u16(raw, 20) << 16)
                sz = u32(raw, 28)
                return off, [x for x, _ in lfn], cl, sz
            lfn = []
        return None

    @staticmethod
    def lfn_name(raw):
        # LFN 的 13 个 UTF-16 字符分布在 1..10 / 14..25 / 28..31
        chunks = raw[1:11] + raw[14:26] + raw[28:32]
        chars = []
        for i in range(0, len(chunks), 2):
            c = chunks[i] | (chunks[i + 1] << 8)
            if c in (0x0000, 0xFFFF):
                break
            chars.append(chr(c))
        return "".join(chars).encode("utf-8", "replace")


# --------------------------------------------------------------------------
# 主流程
# --------------------------------------------------------------------------
def patch_partition(buf):
    """就地修改 2.5MB 的 /setting 镜像，返回改动描述列表。"""
    fat = Fat(buf)
    changes = []
    info = {
        "fat_bits": fat.bits,
        "cluster_bytes": fat.cluster_bytes,
        "clusters": fat.count,
    }

    # 1) mode 子目录
    mode = fat.lookup(b"MODE")
    if mode is None:
        raise SystemExit("在 /setting 根目录里找不到 MODE 目录，镜像可能不是 /setting")
    mode_off, _, mode_cluster, mode_size = mode
    is_dir = (buf[mode_off + 11] & 0x10) != 0
    if not is_dir:
        raise SystemExit("MODE 不是目录？镜像结构和预期不符")

    # 2) dmode
    hit = fat.lookup(b"DMODE", mode_cluster)
    if hit is None:
        raise SystemExit("找不到 /mode/dmode —— 可能已经被删干净（删掉也是对的，开机默认 mode3）")
    dm_off, dm_lfn, dm_cluster, dm_size = hit
    target = DMODE_TARGET[b"DMODE"]
    if len(target) > fat.cluster_bytes:
        raise SystemExit("目标内容比簇还大")
    old = bytes(buf[fat.cluster_off(dm_cluster):fat.cluster_off(dm_cluster) + max(dm_size, 1)])
    if old[:len(target)] == target and dm_size == len(target):
        changes.append(("dmode 已经是正确内容，跳过", 0))
    else:
        coff = fat.cluster_off(dm_cluster)
        buf[coff:coff + len(target)] = target
        struct.pack_into("<I", buf, dm_off + 28, len(target))
        changes.append(("dmode: %r(%d 字节) -> %r(%d 字节)"
                        % (old[:dm_size], dm_size, target, len(target)), coff))

    # 3) 删除 env.txt / ldtest.so
    for nm in DELETE_NAMES:
        h = fat.lookup(nm)
        if h is None:
            changes.append(("%s 不存在，跳过" % nm.decode(), 0))
            continue
        off, lfn_offs, cl, sz = h
        freed = fat.free(cl) if cl else 0
        for lo in lfn_offs:
            buf[lo] = 0xE5
        buf[off] = 0xE5
        changes.append(("delete %s (%d 字节, %d 簇, %d 个 LFN)"
                        % (nm.decode(), sz, freed, len(lfn_offs)), off))
    return changes, info


def dump_region(dump, base, size, out_path):
    flat = dump.read_flat(base, size)
    with open(out_path, "wb") as f:
        f.write(flat)
    return flat


def main(argv):
    ap = argparse.ArgumentParser(description="修补 NEX-7 /setting 分区里的 dmode 等文件")
    ap.add_argument("--in", dest="inp", help="输入 dump（编程器读出的原始镜像）")
    ap.add_argument("--out", dest="out", help="输出的修好后的 dump")
    ap.add_argument("--oob", type=int, default=64, help="每页备用区字节数；纯数据镜像填 0（默认 64）")
    ap.add_argument("--base", default="0x420000", help="分区起始偏移（默认 0x420000）")
    ap.add_argument("--size", default="0x280000", help="分区长度（默认 0x280000）")
    ap.add_argument("--report", default=None, help="写一份变更报告")
    ap.add_argument("--extract", default=None, help="额外把修好后的 /setting 导出成 vfat 镜像")
    ap.add_argument("--selftest", action="store_true", help="自检")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    if not args.inp or not args.out:
        ap.error("需要 --in 和 --out")
    base = int(args.base, 0)
    size = int(args.size, 0)

    with open(args.inp, "rb") as f:
        raw = f.read()
    dump = Dump(raw, args.oob, base)

    need = base + size
    span = (need + PAGE - 1) // PAGE * (PAGE + args.oob) if args.oob else need
    if len(raw) < span:
        raise SystemExit("dump 太小：%d 字节，至少需要 %d（--oob %d）" % (len(raw), span, args.oob))

    flat = bytearray(dump.read_flat(base, size))
    if flat[510] != 0x55 or flat[511] != 0xAA:
        raise SystemExit("0x%X 处不是 vfat 引导扇区（没有 55AA）—— 偏移或 --oob 可能不对，"
                         "请先确认分区位置，不要盲改" % base)

    before = bytes(flat)
    changes, info = patch_partition(flat)
    if bytes(flat) == before:
        print("没有任何改动（可能已经修过了）")
    dump.write_flat(base, bytes(flat))

    with open(args.out, "wb") as f:
        f.write(bytes(dump.data))

    # 报告
    lines = []
    lines.append("输入: %s (%d 字节)" % (args.inp, len(raw)))
    lines.append("输出: %s (%d 字节)" % (args.out, len(dump.data)))
    lines.append("分区: base=0x%X size=0x%X oob=%d" % (base, size, args.oob))
    lines.append("文件系统: FAT%d, 簇 %d 字节, %d 个簇"
                 % (info["fat_bits"], info["cluster_bytes"], info["clusters"]))
    lines.append("")
    offs = [o for _, o in changes if o]
    diffs = [i for i in range(size) if flat[i] != before[i]]
    lines.append("改动字节数: %d" % len(diffs))
    for c, o in changes:
        lines.append("  - " + c)
    if diffs:
        blocks = sorted({(base + i) // BLOCK for i in diffs})
        pages = sorted({(base + i) // PAGE for i in diffs})
        lines.append("")
        lines.append("受影响页(2048B): %s" % ", ".join(str(p) for p in pages))
        lines.append("受影响擦除块(128KB): %s" % ", ".join(str(b) for b in blocks))
        phys = sorted({dump.phys(base + i) for i in diffs})
        lines.append("物理偏移范围: 0x%X - 0x%X" % (phys[0], phys[-1]))
        if len(blocks) > 4:
            lines.append("注意: 改动跨了 %d 个块，写回时建议整片写" % len(blocks))
    text = "\n".join(lines)
    print(text)
    if args.report:
        with open(args.report, "w", encoding="utf-8") as f:
            f.write(text + "\n")
    if args.extract:
        with open(args.extract, "wb") as f:
            f.write(bytes(flat))
        print("已导出修好的 /setting 镜像: %s" % args.extract)
    return 0


# --------------------------------------------------------------------------
# 自检：造一个和真相机同构的 vfat 镜像（2.5MB / 簇 16KB / FAT12）
# --------------------------------------------------------------------------
def make_test_volume():
    total = SETTING_SIZE
    bps, spc, rsvd, nfats, root_ents, fatsz = 512, 32, 1, 2, 512, 1
    tot_sectors = total // bps
    buf = bytearray(total)
    buf[0:3] = bytes([0xEB, 0x3C, 0x90])
    buf[3:11] = b"MSWIN4.1"
    struct.pack_into("<H", buf, 11, bps)
    buf[13] = spc
    struct.pack_into("<H", buf, 14, rsvd)
    buf[16] = nfats
    struct.pack_into("<H", buf, 17, root_ents)
    struct.pack_into("<H", buf, 19, tot_sectors)
    buf[21] = 0xF8
    struct.pack_into("<H", buf, 22, fatsz)
    struct.pack_into("<H", buf, 24, 32)   # sectors/track
    struct.pack_into("<H", buf, 26, 2)    # heads
    struct.pack_into("<I", buf, 28, 0)    # hidden
    struct.pack_into("<I", buf, 32, 0)    # total32
    buf[38] = 0x29
    struct.pack_into("<I", buf, 39, 0x12345678)
    buf[43:54] = b"SETTING    "
    buf[54:62] = b"FAT12   "
    buf[510] = 0x55
    buf[511] = 0xAA
    fat = Fat(buf)

    state = {"next": 2}

    def alloc(nclusters):
        first = state["next"]
        for i in range(nclusters):
            c = first + i
            fat.fat_set(c, c + 1 if i < nclusters - 1 else 0x0FFF)
        state["next"] = first + nclusters
        return first

    def put_file(dir_off, slot, name8, ext, data):
        ncl = max(1, (len(data) + fat.cluster_bytes - 1) // fat.cluster_bytes)
        first = alloc(ncl)
        coff = fat.cluster_off(first)
        buf[coff:coff + len(data)] = data
        e = bytearray(32)
        e[0:8] = name8.ljust(8)[:8].encode()
        e[8:11] = ext.ljust(3)[:3].encode()
        e[11] = 0x20
        e[12] = 0x18  # 小写显示（base + ext）
        struct.pack_into("<H", e, 26, first & 0xFFFF)
        struct.pack_into("<I", e, 28, len(data))
        o = dir_off + slot * 32
        buf[o:o + 32] = e
        return first

    def put_dir(dir_off, slot, name8, ext):
        first = alloc(1)
        e = bytearray(32)
        e[0:8] = name8.ljust(8)[:8].encode()
        e[8:11] = ext.ljust(3)[:3].encode()
        e[11] = 0x10
        e[12] = 0x18
        struct.pack_into("<H", e, 26, first & 0xFFFF)
        o = dir_off + slot * 32
        buf[o:o + 32] = e
        # "." / ".."
        coff = fat.cluster_off(first)
        for i, (n8, cl) in enumerate(((b".          ", first), (b"..         ", 0))):
            d = bytearray(32)
            d[0:11] = n8
            d[11] = 0x10
            struct.pack_into("<H", d, 26, cl & 0xFFFF)
            buf[coff + i * 32:coff + i * 32 + 32] = d
        return first

    root = fat.root_off
    put_file(root, 0, "HASP", "", bytes(range(88)))
    put_file(root, 1, "BACKUP", "BIN", b"B" * 500736)
    put_file(root, 2, "DMMCONFI", "BIN", bytes([0xA5]) * 70865)
    put_dir(root, 3, "APPFW_IN", "FRA")
    put_file(root, 4, "ENV", "TXT", b"LD_PRELOAD=/setting/ldtest.so")
    put_file(root, 5, "FACEDMY", "BIN", bytes([7]) * 51200)
    put_dir(root, 6, "GPS", "")
    put_file(root, 7, "KEMCO", "TXT", b"k" * 3562)
    put_file(root, 8, "LDTEST", "SO", bytes([0x7f, 0x45, 0x4c, 0x46]) * 39747)
    put_dir(root, 9, "MODE", "")
    put_file(root, 10, "PUSH_TES", "TXT", b"0123456789abcdef")
    put_file(root, 11, "ULOGIO", "BIN", bytes([3]) * 2620)
    put_dir(root, 12, "UPDATER", "")

    mode = fat.lookup(b"MODE")
    mode_cluster = u16(buf, mode[0] + 26)
    mo = fat.cluster_off(mode_cluster)
    d = bytearray(32)
    d[0:8] = b"DMODE   "
    d[8:11] = b"   "
    d[11] = 0x20
    d[12] = 0x18
    cl = alloc(1)
    struct.pack_into("<H", d, 26, cl & 0xFFFF)
    struct.pack_into("<I", d, 28, 1)
    buf[mo + 64:mo + 96] = d          # 跳过 . 和 ..
    buf[fat.cluster_off(cl)] = ord("x")
    return bytes(buf)


def selftest():
    import tempfile
    ok = True

    def check(cond, msg):
        nonlocal ok
        print(("  [OK]   " if cond else "  [FAIL] ") + msg)
        if not cond:
            ok = False

    print("== 1) 造测试卷 ==")
    vol = make_test_volume()
    check(len(vol) == SETTING_SIZE, "卷大小 2.5MB")
    fat = Fat(vol)
    check(fat.bits == 12, "识别为 FAT12（簇数 %d）" % fat.count)
    check(fat.cluster_bytes == 16384, "簇 16KB")
    hit = fat.lookup(b"DMODE", u16(vol, fat.lookup(b"MODE")[0] + 26))
    check(hit is not None, "找到 /mode/dmode")
    check(vol[fat.cluster_off(hit[2]):fat.cluster_off(hit[2]) + 1] == b"x", "原始内容为 'x'")

    print("== 2) 打包成两种 dump（flat / oob=64）==")
    tmp = tempfile.mkdtemp()
    for oob in (0, 64):
        dump_bytes = bytearray((SETTING_BASE + SETTING_SIZE + PAGE) * (PAGE + oob) // PAGE)
        d = Dump(dump_bytes, oob, SETTING_BASE)
        d.write_flat(SETTING_BASE, vol)
        inp = os.path.join(tmp, "dump_oob%d.bin" % oob)
        outp = os.path.join(tmp, "fixed_oob%d.bin" % oob)
        rep = os.path.join(tmp, "report_oob%d.txt" % oob)
        with open(inp, "wb") as f:
            f.write(bytes(d.data))
        print("== 3) 打补丁 (oob=%d) ==" % oob)
        rc = main(["--in", inp, "--out", outp, "--oob", str(oob), "--report", rep])
        check(rc == 0, "退出码 0")
        with open(outp, "rb") as f:
            fixed = Dump(f.read(), oob, SETTING_BASE).read_flat(SETTING_BASE, SETTING_SIZE)
        ffat = Fat(fixed)
        mh = ffat.lookup(b"MODE")
        mcl = u16(fixed, mh[0] + 26)
        dh = ffat.lookup(b"DMODE", mcl)
        check(dh is not None, "dmode 还在")
        size = u32(fixed, dh[0] + 28)
        content = bytes(fixed[ffat.cluster_off(dh[2]):ffat.cluster_off(dh[2]) + size])
        check(content == b"3\n", "dmode 内容 == b'3\\n' (实际 %r)" % content)
        check(size == 2, "目录项长度 == 2")
        check(ffat.lookup(b"ENV.TXT") is None, "env.txt 已删除")
        check(ffat.lookup(b"LDTEST.SO") is None, "ldtest.so 已删除")
        dh2 = ffat.lookup(b"DMMCONFI.BIN")
        check(dh2 is not None and bytes(fixed[ffat.cluster_off(dh2[2]):ffat.cluster_off(dh2[2]) + 16]) == bytes([0xA5]) * 16,
              "DmmConfig.bin 保留且内容未变")
        bh = ffat.lookup(b"BACKUP.BIN")
        bcl = bh[2]
        bdata = bytes(fixed[ffat.cluster_off(bcl):ffat.cluster_off(bcl) + bh[3]])
        check(bdata == b"B" * 500736, "Backup.bin 内容未变")
        check(ffat.chain(u16(fixed, ffat.lookup(b"LDTEST.SO")[0] + 26)) == []
              if ffat.lookup(b"LDTEST.SO") else True, "ldtest.so 簇链已释放")
        # 老 LDTEST 的簇应该已空闲
        orig_cl = fat.lookup(b"LDTEST.SO")[2]
        check(ffat.fat_get(orig_cl) == 0, "原 ldtest.so 首簇在 FAT 里已清零")

    print("== 4) 用 pyfatfs 独立校验 ==")
    try:
        sys.path.insert(0, os.path.join("nex7", "pylibs"))
        from pyfatfs.PyFatFS import PyFatFS
    except Exception as e:  # noqa
        print("  [skip] pyfatfs 不可用: %r" % (e,))
        PyFatFS = None
    if PyFatFS is not None:
        for oob in (0, 64):
            p = os.path.join(tmp, "fixed_oob%d.bin" % oob)
            with open(p, "rb") as f:
                fixed = Dump(f.read(), oob, SETTING_BASE).read_flat(SETTING_BASE, SETTING_SIZE)
            vp = os.path.join(tmp, "vol_oob%d.img" % oob)
            with open(vp, "wb") as f:
                f.write(fixed)
            try:
                fs = PyFatFS(vp, read_only=True)
                names = [str(x).upper() for x in fs.listdir("/")]
                check(not any("ENV.TXT" in n for n in names), "pyfatfs 视角 env.txt 已消失")
                data = None
                for p in ("/MODE/DMODE", "/mode/dmode", "/Mode/dmode"):
                    try:
                        with fs.openbin(p) as fh:
                            data = fh.read()
                        break
                    except Exception:
                        continue
                if data is None:
                    raise RuntimeError("pyfatfs 找不到 dmode（试过 /MODE/DMODE 等路径）")
                check(data == b"3\n", "pyfatfs 读到 dmode == b'3\\n' (%r)" % data)
                try:
                    fs.close()
                except Exception:
                    pass
            except Exception as e:
                check(False, "pyfatfs 打开失败: %r" % (e,))

    print("")
    print("SELFTEST %s" % ("PASSED" if ok else "FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
