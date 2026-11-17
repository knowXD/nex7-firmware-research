# 离线刷机包：清单、验收、前置条件

> 一页看清"哪些包能用、刷之前要做什么、怎么验证"。
> 所有结论都能用文末的验收命令复现，不需要相机。

## 1. 包清单

| 包 | 内容 | 版本 / 模式 | 前置条件 | 验收 |
|---|---|---|---|---|
| `out_stock99` | 原厂 1.03 内容 + 版本 9.99 | 9.99 / U(升级) | 无 | ✅ PASS |
| `out_stock` | 原厂 1.03 原样 | 1.03 / U | 无 | — |
| `out_jpeg_v2` | qscale 0.75（av-cam 0x461092）+ 9.99 | 9.99 / U | 无 | ✅ 结构+字节 PENDING 实拍 |
| `out_scn_v2` | scenario 纯桩（只写日志） | 1.03 / O(同版本) | 无 | ✅ PASS |
| `out_delegate_v2` | scenario 委托桩（日志 → 调原模块） | 1.03 / O | **必须先把 `orig_video.so` 推到 `/setting/`** | ✅ PASS |
| `out_bitrate8` | libmpr.so 0x4ED990 码率 | 1.03 / O | 无 | ⚠️ 未验证 |
| `out_qscale` / `out_avcbits` / `out_bitrate` / `out_bitrate2` / `out_jpeg_all` / `out_jpeg50` / `out_mod` / `out_test*` | 历史实验包 | — | — | 已被 v2 取代 |

> 版本字段在 FDAT 头 [32]=minor、[33]=major，按十六进制显示：
> `minor=0x99` 就是 **9.99**，`0x03/0x01` 是 **1.03**。
> 显示里那个 `0100` 是格式字段，不是版本号（早期容易被误读）。

## 2. 一键验收

`nex7/hack/verify_packages.py` 把「包 → tar → 镜像 → 模块」四层串成一条命令：

```bat
python nex7\hack\verify_packages.py ^
  --tar nex7\new_delegate2.tar ^
  --dat nex7\out_delegate_v2\firmware_packed.dat ^
  --stub nex7\hack\scn_delegate_v2_padded.so
```

它检查四件事：

1. **.dat 头**：机型必须是 NEX-7 `0x12030024`，版本/模式打印出来；
2. **TPZL 结构**：nflasha8 必须是 816 块 × 16 段 × 4096 字节（64KB 块）；
3. **替换窗口**：解出第 209 块（0xD10000–0xD20000），比对 `0xD1C400` 起的 11516 字节
   是否与期望的 .so 逐字节一致；
4. **sum 校验**：tar 里 `*.sum` 记录的 crc32/size 是否与成员实际值一致。

四条全过才打印 `PASSED`。

## 3. 刷之前必须做的三件事

1. **备份 /setting 里的关键文件**（dmode、env.txt 现状），至少 pull 一份到电脑；
2. **先刷 `out_stock99`**，确认"能刷、能启动"，再考虑功能包；
3. **只有刷 delegate 包需要第 4 步**：

```bat
:: 把原 scenario 模块放到 /setting/orig_video.so（delegate 桩靠它把调用转回去）
python pmca-console.py updatershell -m NEX-7 -d native
> push nex7\hack\orig_video.so /setting/orig_video.so
> exit
```

`nex7/hack/orig_video.so` 就是从官方 nflasha8 里取出来的 `scenario/AVBB_SCN_START_VIDEO.so`
（11516 字节，SHA256 `8FEDCB26AA574AD209121A47D39AB09F5AC7C5E6BA9BB6E3CBCB5AC6A407D7BC`）。

**不推也行**：桩会写一行 `dlopen(...) FAILED` 到 `/setting/scn_test.log` 然后返回 0，
录像用不了但不会把上层状态机推进错误分支。

## 4. v2 桩相对 v1 改了什么（为什么重新打包）

| 改动 | 原因 |
|---|---|
| 委托失败时返回 **0** 而不是 -1 | 无法在真机验证 -1 会走哪条错误分支；返回 0 至少不破坏调用方状态机 |
| 日志改成 **O_APPEND**，三种情况分开写 | 多次触发不互相覆盖，能一眼看出卡在 dlopen 还是 dlsym |
| 链接参数加 `-Wl,-z,max-page-size=0x1000` | v1 的 PT_LOAD 之间有 64KB 空洞（vaddr 0/0x10290/0x20380），
  现在各段 **vaddr == p_offset**，即使加载器只会"整个文件平铺"也能正确映射 |
| 加 `-fno-asynchronous-unwind-tables` | 去掉 `__aeabi_unwind_cpp_pr0` 这个没必要的未定义符号，
  现在 delegate 只剩 `dlopen`/`dlsym` 两个未定义、stub 一个都没有 |

## 5. 已经排除的疑点：`sid` 的位置

- 各 scenario 模块的 `sid` 地址都不一样：`0x9130 – 0x9a2c`（START_VIDEO 是 0x94fc）；
- 加载器 `libtestcmd_scn.so` 里**没有** `sid` 这个字符串，只 dlsym `scenario_run`；
- 所以不可能有"按固定偏移读 sid"的代码；
- 我们的桩导出 `scenario_run`（必须）+ `sid`（跟原始同值 0x010A0000），放在哪个偏移都无所谓。

## 6. 仍然必须等相机的部分

- 桩能不能被 Sony 的自定义加载器（`libsonydl.so`）接受 —— 只能上机试；
- `int scenario_run(uint8_t*, int)` 的 ABI 是否如我们反汇编所见 —— 只能上机试；
- 首次 `scn_test.log` 是否出现 —— 这是"链路通了"的唯一证据。

## 7. 复现构建

```powershell
# 1) 编译（zig 的缓存要留在工作区内，否则沙箱下会 AccessDenied）
$env:ZIG_GLOBAL_CACHE_DIR = "nex7\zigcache\global"
$env:ZIG_LOCAL_CACHE_DIR  = "nex7\zigcache\local"
nex7\zigpkg\ziglang\zig.exe cc -target arm-linux-musleabi -shared -fPIC -nostdlib -nodefaultlibs -O2 ^
  -fno-asynchronous-unwind-tables -fno-unwind-tables -Wl,-z,max-page-size=0x1000 ^
  -o nex7\tmp\scn_delegate.so nex7\hack\scn_delegate.c -L nex7\hack -lsonydl

# 2) 补齐到 11516 字节
python nex7\hack\elf_pad.py nex7\tmp\scn_delegate.so nex7\hack\scn_delegate_v2_padded.so 11516

# 3) 打镜像 → 压缩 → 打 tar → 打包（等同于 nex7\hack\build_scn_pkg.ps1 的四步）

# 注意：本机 PowerShell 默认禁止运行 .ps1（ExecutionPolicy），直接 & 脚本会报
#   "在此系统上禁止运行脚本"。把 build_scn_pkg.ps1 里的四步复制成内联命令跑即可，
#   或者先 Set-ExecutionPolicy -Scope Process Bypass。
```
