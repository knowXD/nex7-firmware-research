# NEX-7 固件关键偏移速查

所有偏移基于官方 1.03 固件解包结果（nex7/unpacked/）。

## av-cam.bin（/system 分区，nflasha3 内）

| 偏移 | 内容 | 备注 |
|---|---|---|
| 0x31e71c | Creative Style 名称块 | Vivid/Neutral/Portrait/Landscape/BW/Clear/Deep/Light/Sunset/Nightview/Autumnleaves/Real/Sepia/Standard（NEX-6 同内容，位于 0x368988） |
| 0x461092 | JPEG 量化表（luma 64B + chroma 64B） | 标准 Annex K 表，zigzag 顺序 |
| 0x46114f | 字符串 "dgi_jpeg_qtable_calc_qscale" | JPEG 编码器 qscale 计算 |
| 0x2b7900 附近 | "ExCodecEncMp4.cpp" | MP4 编码器模块 |
| 0x2b7a10 | 码率常量表 | 4004, 240000, 16M, 12M, 9M, 18M, 10M, 3M |
| 0x2b7e44 | 另一组码率常量 | 16M, 6M, 18M, 12M, 9M |
| 0x1e9bf7 | 字符串 "encodeQuality" | |
| 0x24d984 | 字符串 "pictureQuality" | |
| 0x2f324e | 字符串 "Invalid Jpeg Quality" | 质量校验 |

## libmpr.so（/usr/lib）

| 偏移/符号 | 内容 |
|---|---|
| 0x4ed990 | 28,000,000 / 24,000,000 / 18,000,000 / 90,000 常量（RecInfo 日志函数内比较用） |
| MprIf::EncodeStill | JpgInfo 结构：+0x68、+0x74、+0x80 字段被复制 |

## libObj.so（/usr/lib）

| 符号 | 内容 |
|---|---|
| UtilStillSize::GetStillTargetFileSize | 0x127079，按 JpgQuality 估算文件大小 |
| JPG_QUALITY_STD / FINE / EXFINE | 框架支持三档，菜单只暴露两档 |
| VdfCh setter 族 | setPeaking/setZebra/setFaceFrame/setDisplayQuality… 均为 GLOBAL |
| ObjRenderer SetZebra | [onoff=%d, gray=%d, disp=%d] |

## init（initrd.img 内 /sbin/init）

| 偏移 | 内容 |
|---|---|
| 0x8a30 | 解析 /setting/mode/dmode；文件存在即 config[0]=1 |
| 0x8bd2 | 解析 /setting/sen/smode |
| 0x8c92 | parse_and_set_env：KEY=VALUE → putenv，无等号 → unsetenv |
| 0x8d8e | 加载 /setting/env.txt |
| 0x9272 | 判断 config[0]，决定是否调用 env 解析 |
| 0x9276 | beq 0x927c（想强制加载 env.txt 可改 nop） |

## Backup.bin 属性

| ID | 含义 |
|---|---|
| 0x003c0373..75 | recLimit（时/分/秒） |
| 0x01070148 | palNtscSelector |
| 0x010d008f+i (i=0..34) | language |
| 0x003e0005 | modelName（"NEX-7"） |
| 0x00e70000 | modelCode |
| 0x00e70003 | serialNumber |

## 固件包结构

- firmware.tar 成员：0100_config、0110_backup、0300_partconf、0600_gps、0700_part_image、0800_appli、1630_ca + 对应 *_sum
- /system（nflasha3）= vmlinux.bin + initrd.img + av-cam.bin + sabin/lensbin
- /usr（nflasha8）= ext2，应用层
- 校验：每个成员 CRC32 记录在 *_sum/*.sum；FDAT 头 CRC32；CXD4132 用 AES-ECB 加密
## radare2 分析结果（av-cam.bin，Thumb）

| 偏移 | 内容 |
|---|---|
| 0x31e390 | 风格名拷贝函数：style id(0..14) → 名称字符串（"Vivid"/"Neutral"/…），跳表在 0x31e3a4 |
| 0x31e4b2 | 风格 ID → 内部色彩模式码映射（0xc/0x2/0x3/0x6/0xd/0xe/0xf/0x4/0x5/0x10/0x11…），跳表在 0x31e4c4 |
| 0x250578 | 通用参数设置函数：表记录 12 字节 {+4:u16 id, +6:u16, +8:u32, +0xc:value}，按 id 查找后写值 |
| 0x31e506 | 调用参数设置：id 0xb029、0x2005 等 |

结论：Creative Style 的“名字”和“ID→内部码”在 av-cam 里，
但真正的色彩矩阵/曲线由下游 ISP 参数表（id 0xb029/0x2005…）决定，
不在 av-cam 的显式数据表中，需要继续追参数表的定义位置。
### 追加：参数表与 Creative Style 的下发路径

- 参数表指针 = 上下文结构 +0x3c（运行时分配，非静态数组）；
- set_param(0x250578) 在表内按 12 字节记录查找 u16 id（共 0x29=41 条），写入 +0xc 的值；
- Creative Style 函数（0x31e390 起）会批量设置：0xb029、0x2005、0x2000 等参数；
- 风格 ID(0..14) → 内部色彩模式码的映射在 0x31e4b2（跳表 0x31e4c4）；
- 结论：av-cam 只负责把“风格码 + 参数”下发给 ISP；真正的 CCM/曲线在 ISP 侧，
  不在 av-cam 的显式数据表中。要改色彩，需要动 ISP 固件或其默认参数表。
## TPZL 关键格式（血的教训）

- 每个 64KB 块必须由 **16 个 4096 字节的分段**组成；
- 每段是独立的 LZ77 流（0xF0）或存储段（0x0F + 长度 4096 + 原始数据）；
- LZ 窗口 4095 字节，正好一个分段——匹配不能跨段；
- 每段自带结束标记（0x00 0x00），不能只在整个块末尾写一个；
- 违反这条，fwtool 能解，但相机引导程序挂载 /system 失败 → 变砖。
## JPEG 质量控制的最终结论（2026-11-12）

### 关键事实

- av-cam 的运行基址：**0xC3421000**（由字符串指针反推确认）；
- JPEG 采样：**4:2:2**（Y=2x1，Cb/Cr=1x1），不是 4:2:0；
- 存储的 6 份量化表（0x461092、0x500464、0x5097F4、0x50FC60、0x536E24、0x555D64）
  **不参与静止图像编码**，改它们无效；
- 量化表是运行时算的：`dgi_jpeg_qtable_calc_qscale` @ **0x6D01C**（Thumb），
  公式 (base * scale + 50) / 100，scale 由质量决定（STD 约为 FINE 的 2 倍）。

### 有效补丁（已验证）

- 位置：**0x6D032**，2 字节；
- 原指令：`mov r7, r0`（07 46）；
- 新指令：`lsrs r7, r0, #1`（47 08），把缩放系数减半；
- 效果：
  - STD 量化均值 10.12 → 5.06（等于原厂 FINE）
  - FINE 量化均值 5.06 → 2.77（接近隐藏的 EXFINE）
  - 文件体积：STD +70%，FINE +59%

### 补丁包

- `nex7/out_qscale/firmware_packed.dat`（verskip 模式，版本 1.03）
- 回滚包：`nex7/out_verskip/firmware_packed.dat`

### verskip

- FDAT 头 modeType 改为 'O' 可跳过版本比较；
- fwtool 打包时设置环境变量 `FWTOOL_UPDATE_MODE=O`；
- 已实测：9.99 → 1.03 降级刷写成功，版本不锁死。
## 视频码率（2026-11-12 进行中）

### 已排除

- av-cam 里的常量组（0x2B7A10：4004、240000、16M、12M、9M、18M、10M、3M）**不是码率控制点**；
  把 16M→46M、12M→46M 刷入后，实测：
  - AVCHD PS 50p：25.11 Mbps（无变化）
  - AVCHD FX：20.78 / 22.36 Mbps（无变化）
  - MP4 1440：12.13 / 12.14 Mbps（无变化）
- 这组常量属于 `ExCodecEncMp4.cpp` 模块，可能是缓冲/上限参数。

### 真正的控制点（待验证）

- 应用层 `nflasha8` 的 `libmpr.so` 内：
  - libmpr.so 文件偏移 **0x4ED990**：28,000,000 / 24,000,000 / 18,000,000
  - 对应 nflasha8 镜像文件偏移 **0x2548590**
  - 旁边的调试字符串：`RecoringRate : 28Mbps / 24Mbps / 18Mbps`，源文件 `IF/hdAvcIfo_Rec.cpp`
  - 即 AVCHD 的 PS/FX/FH 录制码率表；
- 已制作补丁：28M→46M、24M→46M、18M→30M；
- 另有 MP4 相关表：libmpr.so **0x6E9D44**（9M/6M/3M）与 0x6E9D6C（8.81M/5.81M/2.81M）。

### 待刷入的包

`nex7/out_bitrate8/firmware_packed.dat`
（verskip，版本 1.03，nflasha3=qscale，nflasha8=码率补丁；已通过结构校验，**尚未刷入**）

### 打包流程（nflasha8）

1. 直接改 `nflasha8_unpacked` 镜像内嵌 ext2 的字节（同尺寸原地改，无需重建文件系统）；
2. `tpzl.exe` 重新压缩（816 块 × 16 × 4096，输出约 25.9MB）；
3. `fw_build.py --replace-member` 同时替换 nflasha3 与 nflasha8，自动更新 part_image.sum；
4. `FWTOOL_UPDATE_MODE=O` 打包 verskip。

### 刷写注意事项

- 相机在 `Low battery` 时会拒绝刷写（门禁保护，无害）；
- Windows 主机在切换升级模式后有时会 `DeviceIoControl 31` 崩溃，相机留在升级模式，重跑同一命令即可继续写入；
- 切换模式需要用户在相机屏幕上按确认键（提示“是否恢复相机默认设置”）。
## 应用层（nflasha8）改造空间（2026-11-13 发现）

### 已验证可安全刷写

- nflasha8 镜像可原地改字节（内嵌 ext2，同尺寸），tpzl 重新压缩（816 块 × 16 × 4096），
  fw_build 双成员替换 + sum 更新，刷入后相机启动正常。

### 码率调查的最终结论（全部无效）

| 位置 | 结果 |
|---|---|
| av-cam MP4 常量 16M/12M（0x2B7A18/0x2B7A1C） | 无效果 |
| nflasha8 libmpr 表 28M/24M/18M（镜像 0x2548590） | 无效果 |
| av-cam AVC 字面量 24M/18M（0xF97E0、0x35B730、0xF93BC、0xFA57C） | 无效果 |

实测始终 22–26 Mbps。编码器为 av-cam 内 MojitoAvcEncoder，
质量信息走 RecvAvcEncSetMovieQualityInfoComp，码率上限疑似在编码器核心/微码内。

### 应用层里发现但未做的功能

- **Zebra**：libObj 有 ExecCommandSetZebra、MSGID_SET_ZEBRA_CMD（60 处）；
- **HDMI 分辨率**：PARAMID_HDMI_RESO_DATA（198 处）；
- **录制时长限制**：MprCtrl::GetRecLimitTime、MovieRecEtcDef::CALLBACK_FACTOR_REC_LIMIT_TIME；
- 相关符号：MprIf::SetRecLimitTimeInfo（PLT 0x179C7B）。

### 当前相机状态

- 固件：qscale 补丁 + 4 处 AVC 字面量补丁（后者无行为影响），版本 1.03；
- 包：nex7/out_avcbits（当前）、nex7/out_bitrate8（含 nflasha8 补丁）、nex7/out_verskip（原厂回滚）。
## 录制时长限制解除（2026-11-13 成功）

- 属性：Backup ID 0x003C0373–0x003C0375（3 字节：时、分、秒）；
- 原值：00 1D 32 = 29分50秒；
- 新值：0D 01 00 = 13小时01分00秒；
- 操作：updatershell（升级模式）中执行
  `bk w 0x003c0373 0d`、`bk w 0x003c0374 01`、`bk w 0x003c0375 00`、`bk s`；
- 结果：相机显示可录 380 分钟（受卡容量限制），限制解除；
- 实现依据：PMCA-RE tweaks.py 的 RecLimitTweak（onValue [13,1,0]）；
- 注意：写 Backup 需要进升级模式（bk 命令仅在 BackupPlatformBackend 下可用）。
## 2026-11-13 夜：设置层实验记录

### Clean HDMI 尝试（失败，已回滚）

- 属性 0x01070087（编码格式），原值 03 (AVCHD)；
- 按 NEX-5N 社区方法改为 0A (XAVC，不支持)，写入成功；
- 结果：NEX-7 按录制键后 UI 消失、整机无响应，只能拔电池；
- 已写回 03，相机恢复；
- 结论：NEX-7 无“不支持编码格式”的兜底逻辑，此方法不可用。

### 已确认的 Backup 属性

- 0x00E70000 modelCode：00 32 82 14 00（产品码 0032821400）
- 0x003E0005 modelName："NEX-7"
- 0x010D008F 语言字节 = 01
- 0x01070148 PAL/NTSC 开关 = 01（已开启，无菜单项）
- 0x01640001 usbAppInstaller：NEX-7 上不存在
- 受保护属性写入需先 `bk unlock`

### HDMI

- 原生支持 1080p / 1080i / Auto（Setup → HDMI Resolution）；
- 录制时画面仍有叠加信息，无 clean HDMI。

### uxc 资源格式（初步）

- string_*.uxc：0x10 起为 u16 相对偏移表，字符串本体在文件后部；
- master_*.uxc（菜单）：多层嵌套 u16 索引表，带 0xFFFF 空位；
- 修改菜单需完整解析器 + 重打包，属独立项目。
## AXFS initrd（2026-11-13 解析结果）

- initrd.img 是 **AXFS (Advanced XIP Filesystem)**，非 cpio；
- 头部：magic 0x48A0E4CD + "Advanced XIP FS"，大端结构；
- 版本 1.9.1，cblock_size 4096，compression 0（zlib），517 文件，3,117,056 字节；
- 超级块字段：files/size/blocks/mmap_size + 18 个区域描述符偏移；
- 区域：strings(0x2F7751, 4143B)、xip(2MB)、byte_aligned(18KB)、compressed(1MB)、
  node_type/index、cnode_offset/index、banode_offset、cblock_offset、
  inode_file_size/name_offset/num_entries/mode_index/array_index、modes/uids/gids；
- 文件名：./ bin dev etc kmod lib log mnt proc root sbin setting sys system tmp usr var、version.txt、ash、busybox、cat...
- 工具：github jaredeh/axfs（mkfs.axfs-legacy + 内核驱动源码，格式定义在 kernel/fs/axfs/axfs_fs.h）；
- 待做：inode 内容提取器、重打包兼容性验证、init 注入。
## AXFS 提取成功与启动流程（2026-11-13 下午）

### 关键发现：表是“平面式”存储

- Sony 的 AXFS 表不是交错 BE32，而是**按字节平面**排列：
  第 k 字节平面位于 fsoff + k*max_index，值 = Σ plane[k][idx] << (8*k)；
- 内核驱动的 bytetable_stitch 被 Sony 改写过；
- 按平面读法验证通过：version.txt 19B、ash 链接、busybox 324,484B/80 页、init 16,876B/5 页。

### 提取结果

- 69 个文件、72 个符号链接、353 个设备节点，落到 nex7/initrd_unpacked/；
- 含 bin/busybox、kmod/*.ko（liro、hdmi、usbcore、usbg_* 等）、lib/libsony*、sbin/init。

### 启动流程（/sbin/init 字符串）

- 读 /setting/mode/dmode、/setting/env.txt、/setting/sen/smode；
- 挂载 compressed /system（失败回退 vfat）、/setting、/usr（ext2 → cramfs → vfat）；
- insmod 内核模块；设置 LD_PRELOAD 调试选项；
- 启动 /usr/bin/sen.elf（另有 bootin.elf 路径）；
- 可选 shell_loop（/dev/ttycons）。

### 潜在注入路径（无需改 AXFS）

- init 的 parse_and_set_env 读取 **/setting/env.txt** 并 putenv；
- /setting 是 vfat 可写分区（nflasha2）；
- 若能让 init 加载我们放置的 LD_PRELOAD 共享库（在 /setting 或 /tmp），即可在启动时执行代码；
- 待验证：env.txt 格式、/setting 写入方式（updatershell 挂载 nflasha2 + push）、最小 ARM .so 的可加载性。
