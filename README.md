# 针对一台已淘汰十多年的相机：索尼 NEX-7 的固件破解

> **EN summary** — A student's attempt to reverse-engineer the firmware of a 2011
> Sony NEX-7 (CXD4132 / BIONZ, 3x ARM11, Linux 2.6.29 RT), with AI assistance.
> **Worked:** JPEG qscale patch, recording-time limit, verskip flashing, NAND partition dump.
> **Didn't:** video bitrate (4 patch sets, zero effect), Android/PMCA (kernel has no binder),
> menus (.uxc is a private format), colour matrices (not located, not verifiable).
> **Stopped at:** SoC and NAND are stacked in one PoP package — going further needs BGA
> rework/programming capability.
> This repository contains documentation, tools and sources only — **no Sony firmware**.

一个学生，用 AI 辅助，破解这台十多年前已淘汰的相机。

十几年前有人试图破解过它，那时候能做的只是改改参数、换换区域设置，工具链还是别人写好的。
现在我想让这台初代专业微单再多做点什么——更高的画质、更长的录制、更合口味的色彩——
但遇到了很大的阻碍。

## 一、目的

验证一件事：一个没有专业逆向背景的学生，用 AI 辅助，能把一台封闭相机的固件做到哪一步。

具体的几个目标：

| 目标 | 原因 |
|---|---|
| 提高 JPEG 画质 | 原厂 FINE 仍有压缩余量 |
| 解除录像时长限制 | 部分区域版本 29:50 就停 |
| 提高视频码率 | 28 Mbps 偏低 |
| 调整色彩 | 想要更接近 A900 或胶片风格 |
| 增加功能 | 例如间隔拍摄 |

## 二、过程

**读固件**：官方更新包 → FDAT 容器 → AES 解密 → TPZL（LZ77，64KB 块）解压 → 内核、initramfs（AXFS）、`/usr`。
分区表：`/setting` 2.5 MB、`/system` 9 MB、`/usr` 42.75 MB 等。

**造工具**：TPZL 分段重建、校验和重算、版本号绕过（verskip），使修改后的固件能重新打包并刷回。

**真机验证**：刷入修改包并实测。JPEG 补丁有效；录像时长有效；视频码率四组补丁全部无效。

**变砖**：为了在不改固件的情况下注入代码，向 `/setting` 写入了 `mode/dmode` 与 `env.txt`，相机无法启动。

**拆机**：拆解后寻找 UART 调试口，并确认了硬件结构——SoC（CXD4132）与 NAND 叠在同一个 PoP 封装内。

固件层面已确认调试串口存在：内核把 `/dev/ttycons` 映射到 `ttyAM0`，init 启动时会无条件在它上面拉起一个 ash shell。
对应到板子上，找到若干 2×2 测试焊盘阵列，其中一个对地为 0Ω。**串口是目前软件层面唯一剩下的入口。**

## 三、结论

### 有效的改动

| 改动 | 结果 |
|---|---|
| JPEG 量化表（av-cam 0x6D032） | STD ≈ 原厂 FINE，FINE ≈ 隐藏的 EXFINE，体积 +60~70% |
| 录像时长 | 29:50 → 13 小时 |
| verskip | 同版本、降级均可刷写 |
| NAND dump | 静态 ARM 工具，可在升级模式下读取分区 |

### 无效或不可行

| 方向 | 结论 |
|---|---|
| 视频码率 | 四组常量补丁均无效；控制点在编码器的速率控制逻辑，不在常量表 |
| Android / PMCA 应用 | 内核中 `binder`、`ashmem`、`logger` 均为 0 次（NEX-6 分别为 137/10/8） |
| 菜单与 UI | `.uxc` 为私有格式，无解析器 |
| 色彩矩阵 | 15 个风格按索引访问，参数表未定位，且无验证条件 |
| 免拆救砖 | 启动标志均位于 NAND |

### 阻碍

若想继续深挖，就得动硬件。

SoC 与 NAND 是 PoP 叠层封装。要读取或改写其中的 NAND，需要把封装拆下来、植球后重焊。
也就是说，**需要具备处理 BGA 封装芯片编程问题的能力**——BGA 返修台、植球手艺，
或者能用的 BGA 转接座/专用编程器。

只靠软件、串口和万用表，到这里就到头了。

## 四、技术细节

| 内容 | 文件 |
|---|---|
| 偏移与结构 | [OFFSETS.md](docs/OFFSETS.md) |
| 固件加密与重组 | [TPZL_FORMAT.md](docs/TPZL_FORMAT.md) |
| 内核与启动 | [KERNEL.md](docs/KERNEL.md) · [KERNEL_MAP.md](docs/KERNEL_MAP.md) |
| 应用层与场景插件 | [APPLAYER_RE.md](docs/APPLAYER_RE.md) |
| av-cam 结构 | [AVCAM_STRUCT.md](docs/AVCAM_STRUCT.md) |
| NAND 分区与 dump | [NAND_DUMP.md](docs/NAND_DUMP.md) |
| 能力清单 | [CAPABILITIES.md](docs/CAPABILITIES.md) |
| 拆机与恢复 | [DISASSEMBLY_UART.md](docs/DISASSEMBLY_UART.md) · [REVIVAL_RUNBOOK.md](docs/REVIVAL_RUNBOOK.md) |
| 工具与源码 | [tools/](tools/) · [src/](src/) |

## 五、仓库说明

- 只有文档、工具源码和一个 ESP32 红外快门触发器；
- 不含任何索尼固件、库或数据包，原始固件请从索尼官网下载；
- 本地备份与构建产物放在 `.lab/`，不提交；
- 文档中每条结论标注证据等级：**[实测]** / **[静态]** / **[推测]**。

## 许可证

- 代码（`tools/`、`src/`、`ir-trigger/`）：MIT
- 文档（`docs/`）：CC BY-SA 4.0
