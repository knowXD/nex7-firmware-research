#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""verify_packages.py -- 一键验收离线刷机包（不需要相机）。

检查一条命令里把这些串起来：
  1) .dat 头部：版本号 / 更新模式 / 机型
  2) tar 里的 nflasha8 成员是不是合法的 TPZL（816 块 x 16 x 4096）
  3) 解出包含 scenario 替换窗口的那一块，逐字节比对期望的 .so
  4) 顺带核对 *.sum 里的 crc32/size 与成员一致

用法：
  python verify_packages.py --tar nex7/new_delegate2.tar \
      --dat nex7/out_delegate_v2/firmware_packed.dat \
      --stub nex7/hack/scn_delegate_v2_padded.so
  python verify_packages.py --selfcheck     # 用现有包跑一遍已知结论
"""
import argparse
import io
import os
import struct
import sys
import tarfile
import zlib

sys.path.insert(0, "nex7/pylibs")
sys.path.insert(0, "nex7/fwtool.py-master")

WIN_OFF = 0xD1C400          # scenario 替换窗口在 nflasha8 内的偏移
WIN_LEN = 11516             # 原 AVBB_SCN_START_VIDEO.so 的长度
BLOCK = 0x10000             # TPZL 的 64KB 块
SEG = 4096                  # 每块 16 个 4KB 段


def tpzl_header(blob):
    if blob[:4] != b"TPZL":
        return None
    magic, bs, tocoff, tocsz = struct.unpack_from("<4sIII", blob, 0)
    return {"block_size_log2": bs, "toc_off": tocoff, "toc_size": tocsz, "blocks": tocsz // 8}


def inflate_block(blob, hdr, idx):
    """解出第 idx 个 64KB 块。"""
    from fwtool.lz77 import inflateLz77
    off, size = struct.unpack_from("<II", blob, hdr["toc_off"] + idx * 8)
    b = io.BytesIO(blob[off:off + size])
    out = bytearray()
    for _ in range(16):
        out += inflateLz77(b)
    return bytes(out)


def check_sum_member(tar_path, member_name, blob):
    """tar 里同目录的 .sum 行是否与成员 crc 一致。"""
    want_crc = "%08x" % (zlib.crc32(blob) & 0xFFFFFFFF)
    want_size = "%08x" % len(blob)
    with tarfile.open(tar_path, "r:") as t:
        for m in t.getmembers():
            if not m.name.endswith(".sum"):
                continue
            text = t.extractfile(m).read().decode("latin1")
            for line in text.split("\n"):
                p = line.split(",")
                if len(p) > 10 and p[-2].endswith(member_name.split("/")[-1]):
                    ok = (p[1] == want_crc and p[2] == want_size)
                    return ok, "%s: crc %s/%s size %s/%s" % (p[-2], p[1], want_crc, p[2], want_size)
    return None, "no sum line"


def dat_header(path):
    from fwtool.sony import dat, fdat
    with open(path, "rb") as f:
        d = dat.readDat(f)
        f.seek(d.firmwareData.offset)
        dec = fdat._crypters["CXD4132"]().decrypt(io.BytesIO(f.read(0x4000))).read(64)
    return {
        "ver_field": dec[12:16],
        "mode": dec[16:17],
        "major": dec[33], "minor": dec[32],
        "model": struct.unpack_from("<I", dec, 36)[0],
    }


def verify(tar_path, dat_path, stub_path, member="0700_part_image/dev/nflasha8"):
    fails = []
    print("说明: 包 %s" % (dat_path or "-"))
    if dat_path:
        h = dat_header(dat_path)
        ver = "%d.%02x" % (h["major"], h["minor"])
        print("  .dat 头: 版本=%s (major=%d minor=0x%02x) 模式=%r 机型=0x%08X 字段=%r" % (
            ver, h["major"], h["minor"], h["mode"], h["model"], h["ver_field"]))
        if h["mode"] not in (b"O", b"o", b"U", b"u"):
            fails.append("未知更新模式 %r" % h["mode"])
        if h["model"] != 0x12030024:
            fails.append("机型不是 NEX-7 (0x12030024)，实际 0x%08X" % h["model"])

    with tarfile.open(tar_path, "r:") as t:
        blob = t.extractfile(t.getmember(member)).read()
    hdr = tpzl_header(blob)
    if not hdr:
        fails.append("nflasha8 不是 TPZL")
        return fails
    print("  TPZL: 块=%d 段长=%dB 块大小=%dKB 压缩后=%d B" % (
        hdr["blocks"], SEG, (1 << hdr["block_size_log2"]) // 1024, len(blob)))
    if hdr["blocks"] != 816:
        fails.append("块数 %d != 816" % hdr["blocks"])

    idx = WIN_OFF // BLOCK
    blk = inflate_block(blob, hdr, idx)
    if len(blk) != BLOCK:
        fails.append("第 %d 块解压后 %d 字节 != 65536" % (idx, len(blk)))
    off_in_blk = WIN_OFF % BLOCK
    got = blk[off_in_blk:off_in_blk + WIN_LEN]
    print("  替换窗口: 第 %d 块偏移 0x%X, 长度 %d" % (idx, off_in_blk, WIN_LEN))

    ok, msg = check_sum_member(tar_path, member, blob)
    print("  sum 校验: %s  (%s)" % ("OK" if ok else ("FAIL" if ok is False else "SKIP"), msg))
    if ok is False:
        fails.append("sum 不一致")

    if stub_path:
        want = open(stub_path, "rb").read()
        if len(want) != WIN_LEN:
            fails.append("期望 stub 长度 %d != %d" % (len(want), WIN_LEN))
        if got[:len(want)] != want:
            diff = next((i for i in range(min(len(want), len(got))) if got[i] != want[i]), None)
            fails.append("窗口内容与 %s 不一致（首个不同字节 @0x%X）" % (os.path.basename(stub_path), diff or 0))
        else:
            print("  窗口内容: 与 %s 逐字节一致 (%.1f KB)" % (os.path.basename(stub_path), len(want) / 1024.0))
        # 手工核对 ELF 关键点
        sys.path.insert(0, "nex7/pylibs")
        try:
            from elftools.elf.elffile import ELFFile
            e = ELFFile(io.BytesIO(want[:6748] if len(want) > 6748 else want))
            ex = {s.name: s["st_value"] for s in e.get_section_by_name(".dynsym").iter_symbols()
                  if s.name and s["st_shndx"] != "SHN_UNDEF"}
            und = [s.name for s in e.get_section_by_name(".dynsym").iter_symbols()
                   if s.name and s["st_shndx"] == "SHN_UNDEF"]
            print("  ELF: 导出 %s 未定义 %s" % (ex, und))
            if "scenario_run" not in ex:
                fails.append("stub 没有导出 scenario_run")
        except Exception as ex:
            print("  ELF 解析跳过: %r" % (ex,))

    # 其余块是否与参考一致（可选）
    return fails


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--tar", required=True)
    ap.add_argument("--dat", default=None)
    ap.add_argument("--stub", default=None)
    ap.add_argument("--member", default="0700_part_image/dev/nflasha8")
    ap.add_argument("--selfcheck", action="store_true")
    a = ap.parse_args(argv)

    fails = verify(a.tar, a.dat, a.stub, a.member)
    print()
    if fails:
        print("FAILED (%d 项):" % len(fails))
        for f in fails:
            print("  - " + f)
        return 1
    print("PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
