# NEX-7 救援手册（工具 / 拆机 / UART / 编程器）

> 目标：把变砖的 NEX-7（SN <serial>，原厂 1.03）救回可开机状态。
> 本文是这一阶段唯一需要照着做的手册；给维修店的那一页是 `REPAIR_NEX7.md`。
> 所有偏移/文件名都来自官方固件本体，不是猜的，出处见第 1 节。

---

## 0. 一页结论

| 项目 | 结论 |
|---|---|
| 相机坏在哪 | 不是硬件坏。`/setting/mode/dmode` 被写成单字节 `x`（0x78），init 解析不出「3」前缀，**应用 sen.elf 根本没启动** |
| 内核/USB 模块 | 正常（init 已经把驱动都 insmod 完了） |
| 为什么黑屏无灯不识别 | 界面、指示灯、USB 海量存储服务全在 sen.elf 里 |
| 最省的修法 | 改回 `dmode = "3"` 并删掉 `/setting/env.txt` |
| 最快的入口 | **UART（ttyAM0）**：init 在启动流程最后**无条件** fork 一个 shell 到 `/dev/ttycons`，所以串口大概率直接给 root shell，一条 `echo 3 > /setting/mode/dmode` 就完事 |
| 次选 | NAND 编程器读出来改 1 字节再写回（要处理 ECC，见第 4 节） |
| 最稳但花钱 | 寄修 / 换主板（约 ¥500，之前干过一次） |

**别做的事**：不要整块擦除 `/setting`、不要重刷固件当「试试看」、不要顺手换主板（除非算下来更划算）。

---

## 1. 根因与证据（为什么敢这么说）

### 1.1 init 的启动顺序（反汇编 `initrd.img` 里的 `/sbin/init`）

```
insmod 驱动（USB 等）
putenv(LD_PRELOAD=...)     ← 由 dmode / env.txt 决定，这里能注入
run_bg_process("/usr/bin/bootin.elf")
if (flag_0x10) run_bg_process("/usr/bin/sen.elf")   ← 应用在这里启动
putenv("LD_PRELOAD=")
fork → shell_loop("/dev/ttycons")                    ← 无条件，串口 shell
```

关键两行（在 `main` 的 0x96e0 附近）：

```asm
0x96e0  ldr r0, [r6, 0x10]     ; appFw 启动标志
0x96e2  cmp r0, 0
0x96e4  beq 0x96ec             ; 标志为 0 → 跳过 sen.elf
0x96e6  adr r0, "/usr/bin/sen.elf"
0x96e8  bl  run_bg_process
0x96ec  ...                    ; 继续往下 → 挂 /setting → shell_loop
```

### 1.2 那个标志由 `/setting/mode/dmode` 的内容决定

`check_mode_file()` 逐字符解析：`'0' / 'k' / 'g' / 'd' / 'e'` 各设一个调试标志，
**`3` 前缀**才把 appFw 标志置 1（对应官方脚本里的「3 = 默认，含 appFw boot」）。

官方脚本
`nex7/unpacked/firmware.tar_unpacked/0700_part_image/dev/nflasha8_unpacked_unpacked/bin/change_mode.sh`：

```
0 : kernel boot
1 : ... global infra
2 : ... LIRO boot
3 : ... appFw boot (**default**)     ← 我们要的值
7/8/9/a/b/d/e : 各种调试变体（3L/3w/3k/3g/3s/3d/3e）
```

脚本写文件用的是 `echo 3 > $MODE_FILE`，即内容为 **`3\n`（0x33 0x0A，2 字节）**。
解析是按字符扫的，所以 `3`（1 字节）和 `3\n`（2 字节）都行；写回时**用 `3\n` 最保险**。

我们写进去的是 `x` → 一个标志都没置上 → sen.elf 不启动 → 黑屏、无灯、USB 不识别。
（旁证：`/setting` 下还留着 `env.txt`(30B) 和 `ldtest.so`(158,988B)，是同一批实验文件。）

### 1.3 init 还会读 `/setting/env.txt` 并 `putenv` 它

`set_oreore_env()` 把 `env.txt` 的内容 mmap 进来直接 putenv。
我们那个 30 字节的 `env.txt` 里是 `LD_PRELOAD=/setting/ldtest.so` ——
即使 dmode 修好了，这一行仍会往 bootin.elf / sen.elf 里预加载我们的测试库，
**测试库一崩，应用还是起不来**。所以 `env.txt` 必须删掉（`ldtest.so` 一并删）。

### 1.4 分区几何（官方 `partinf.conf`）

来源：`nex7/unpacked/firmware.tar_unpacked/0300_partconf/partinf.conf`

```
# start,size,type,flag
nflasha1   0x00020000,0x00400000   (4MB)     ← 升级模式用的 updater 镜像
nflasha2   0x00420000,0x00280000   (2.5MB)   ← /setting（我们出事的）
nflasha3   0x006A0000,0x00900000   (9MB)     ← /system（内核+initrd+av-cam，完好）
nflasha4   0x00FA0000,0x00600000   (6MB)
nflasha5   0x015A0000,0x02400000   (36MB)    ← /wbi
nflasha7   0x039A0000,0x01900000   (25MB)    ← /tmp
nflasha8   0x052A0000,0x02AC0000   (42.75MB) ← /usr（cramfs，完好）
```

NAND 芯片 Toshiba TC58NVG0S3ETA00：128MiB、页 2048+64、块 128KB（0x20000）、共 1024 块。
换算成擦除块：

| 区域 | 字节偏移 | 擦除块（0 起） |
|---|---|---|
| 引导区（loader） | 0x000000–0x020000 | 0 |
| nflasha1 | 0x020000–0x420000 | 1–32 |
| **/setting** | **0x420000–0x6A0000** | **33–52**（20 块） |
| /system | 0x6A0000–0xFA0000 | 53–124 |
| nflasha4 | 0xFA0000–0x15A0000 | 125–172 |
| /wbi | 0x15A0000–0x39A0000 | 173–460 |
| /tmp | 0x39A0000–0x52A0000 | 461–660 |
| /usr | 0x52A0000–0x7D60000 | 661–1002 |
| 未用 | 0x7D60000–0x8000000 | 1003–1023 |

> 注：以上按「无坏块跳过」的线性换算；如果块 0–32 里有坏块，物理位置会整体后移 128KB/块。
> 所以读出来以后**必须验证** 0x420000 处是一个 vfat 引导扇区（0x36 处是 `FAT12   ` 或 `FAT16   `，
> 第 510 字节是 `55 AA`），不能只看偏移就动手。

### 1.5 `/setting` 里有什么（相机活着时 `ls` 出来的）

```
.hasp            88      ← 本机绑定
Backup.bak   500736
Backup.bin   500736      ← 我们已拉取过，就是 nex7/backup_live.bin
DmmConfig.bin 70865      ← 逐机配置（坏点/畸变），别丢
facedmy.bin   51200
kemco.txt      3562
ulogio.bin     2620
appfw_infra/  gps/  mode/  updater/
env.txt          30      ← 我们的（要删）
ldtest.so    158988      ← 我们的（要删）
push_test.txt    16      ← 我们的（无害，可留可删）
```

这些逐机数据（`.hasp`、`DmmConfig.bin`、`facedmy.bin`…）**丢了会掉画质/坏点校正**，
所以「把 /setting 整个擦掉」不是好主意 —— 方案就是改那一个字节。

---

## 2. 三条路线怎么选

| 路线 | 需要的东西 | 难度 | 风险 | 成功率（估计） | 花费 |
|---|---|---|---|---|---|
| **A. UART 串口** | 3.3V USB-TTL + 细烙铁 | 中（焊 2–3 根线到测试点） | 低（先只收不发） | 高。init 结构决定串口大概率直接给 shell | ¥150–300 |
| **B. NAND 编程器** | RT809H + TSOP48 座 + 热风枪 | 高（拆焊 TSOP48、ECC） | 中（ECC 写错读不出来，但有原片 dump 可回滚） | 中高（看店里 ECC 处理能力） | ¥500–900 |
| **C. 寄修/换主板** | 钱 | 无 | 低 | 最高 | ¥300–1000 |

**建议顺序**：

1. 先问自己：**愿不愿意动烙铁**。
   - 不愿意 → 走 C，把 `REPAIR_NEX7.md` 直接发店里（里面写清了只改 1 个字节，别让店里乱来）。
   - 愿意 → 走 A。A 失败（找不到测试点 / 没输出）再考虑 B 或 C。
2. **不要**一上来买编程器（¥500+），A 的成本只有它的三分之一，信息量还最大。

---

## 3. 路线 A：UART（推荐）

### 3.1 原理（2026-11-14 已用 AXFS 解包验证，不是推测）

把 initrd 的 AXFS 镜像解开后，整棵树 516 个 inode 全部枚举出来（22 目录 / 69 普通文件 /
72 符号链接 / **207 字符设备 / 144 块设备** / 2 fifo）。据此确认：

| 环节 | 证据 |
|---|---|
| 设备节点存在 | `/dev/ttyAM0` = 字符设备 **204:16**，权限 0644；`/dev/ttycons -> ttyAM0` |
| 内核有驱动 | vmlinux 里 `cxd4132-uart` / `ttyAM` / `uart-pl011` 都在 |
| 没有 devtmpfs | 内核里搜不到 devtmpfs/devfs → 这些节点是**静态写死在 ramdisk 里**的，不是残留 |
| init 会开它 | `sbin/init`：fork → setsid → `open("/dev/ttycons")` → dup2 ×3 → `execv("/bin/ash")` |
| 无条件执行 | `main` 里 sen.elf 那段之后没有 exit 分支；挂载失败只 printf 然后 `b 0x96ec` 继续 |
| shell 存在 | `/bin/ash`（busybox）在 ramdisk 里 |

**结论：接上 UART 就有一个 root ash shell，不需要 bootloader、不需要拆 NAND。**
（剩下唯一不确定的是波特率：内核 cmdline 由 loader 传，按 115200 → 38400 → 9600 往上试。）
- 有 shell 之后不需要编程器、不需要拆 NAND：

```sh
mount | grep setting          # 确认 /setting 挂着
echo 3 > /setting/mode/dmode  # 一条命令完事（产生 3\n，与官方脚本一致）
rm -f /setting/env.txt /setting/ldtest.so
sync; reboot
```

### 3.2 要买的东西

| 物品 | 规格 | 参考价 | 说明 |
|---|---|---|---|
| USB-TTL 模块 | **CH340 或 CP2102，必须 3.3V** | ¥10–20 | 千万别买 5V 版 |
| 细烙铁 | 尖头 0.5mm，可调温（T12/936） | ¥60–150 | 焊 0.3–0.5mm 测试点 |
| 焊锡丝 | 0.3mm 含松香 | ¥10 | |
| 助焊剂 | 针管装 | ¥10 | 提高成功率，很重要 |
| 漆包线/飞线 | 0.1–0.2mm | ¥10 | 比杜邦线好焊，不会扯掉焊盘 |
| Kapton 胶带 | 5mm | ¥10 | 固定飞线、绝缘 |
| 万用表 | 通断 / 直流电压档 | ¥30–80 | 找 GND/TX 必需 |
| 防静电手环 | 有线即可 | ¥10 | **必买** |
| 精密螺丝刀 | **JIS #00 / #000** | ¥20–50 | 索尼用 JIS，PH 容易滑牙 |
| 塑料撬棒 + 镊子 | 手机维修套装 | ¥20 | 拆排线卡扣 |
| 磁性螺丝垫 | 带分区 | ¥15 | 螺丝别混 |
| 逻辑分析仪（可选） | 8 通道 | ¥20–50 | 波特率猜不出时用 |

**预算 ¥150–300。不要买**：5V 的 TTL、热风枪（这条路用不到）。

### 3.3 拆机（NEX-7 要点）

> 没有 NEX-7 官方维修手册，下面是通用做法 + 这台机器的已知结构。**每一步都拍照**。

1. 拔电池、拔 SD 卡、戴手环。
2. 底面 + 侧面螺丝全拆；**眼罩下面、手柄橡胶下面**通常还有隐藏螺丝。
3. 后盖是卡扣 + 双面胶，从底部缝隙插撬棒慢慢走一圈；**不要用金属撬**（划伤排线/外壳）。
4. 打开后先拍照记排线位置再断开（屏、按键板、EVF）。
5. 目标是**主板正面/背面的测试点**：一般在 SoC（CXD4132）附近、屏蔽罩边上，
   常见 3–4 个并排的裸露焊盘或过孔（丝印可能是 `TP1/TP2`、`CN`、`J`）。

### 3.4 找 GND / TX / RX（万用表法）

1. **GND**：万用表通断档，一表笔接电池负极（或屏蔽罩），另一表笔点候选焊盘，
   响的就是 GND。屏蔽罩本身是 GND。
2. **TX**（相机往外发）：装电池开机的瞬间用**直流电压档**看候选点——
   - 待机 0V 或 3.3V，开机瞬间明显跳动（1.0–2.5V 抖动）→ 就是 TX；
   - 稳定 3.3V 不动 → 电源，别接。
   - **先只接 GND + TX，只收不发**，风险最低。
3. **RX**（要发命令才需要）：TX 找到后，形态相同、上电不跳、电压在 3.3V 附近的往往就是 RX；
   也可以先确认「只收」有日志，再去找 RX。
4. 波特率：**先试 115200 8N1**；不行再试 **38400**（AMBA PL011 内核默认）、57600、9600。
   乱码但看得出结构 → 波特率错，换一档。

### 3.5 接线与首轮抓日志

```
USB-TTL GND  → 相机 GND
USB-TTL RXD  → 相机 TX        （TTL 的 RXD 接相机的 TX）
（确认有输出后）USB-TTL TXD → 相机 RX
USB-TTL VCC  → 不接！
```

1. 先不装电池，线焊好、Kapton 固定，**万用表再确认 GND 对屏蔽罩是通的**。
2. 电脑开串口终端：`putty -serial COM3 -sercfg 115200,8,n,1,N`（或 Tera Term）。
3. 装电池 → 开机（NEX-7 是**拨杆**，不是按键；拨到 ON 保持）。
4. 看输出：
   - **有内核日志**（`Uncompressing Linux...`、init、insmod 之类）→ 成功，等它跑完；
   - **完全没输出** → 换波特率、换 TX 点、检查 RXD/TXD 是否接反；
   - **出现 `sh` 提示符或 `/ #`** → 直接做 3.6。

### 3.6 拿到 shell 之后（照抄）

```sh
cat /setting/mode/dmode ; echo          # 应该看到 x
mount | grep setting                    # 没挂就 mount -t vfat /dev/nflasha2 /setting
echo 3 > /setting/mode/dmode
rm -f /setting/env.txt /setting/ldtest.so
cat /setting/mode/dmode ; echo          # 确认是 3
sync
reboot
```

如果 `/setting` 根本没挂上：

```sh
dosfsck -Y /dev/nflasha2
mount -t vfat /dev/nflasha2 /setting
```

### 3.7 只有日志、没有 shell 怎么办

1. 看日志里有没有 `shell_loop: can not open /dev/ttycons`；
   有的话是 dev 节点问题，可试 `mknod /dev/ttyAM0 c 204 16`。
2. 日志停在 `<<init end>>` 之前 → 卡在更早的地方，拍照发我，按日志继续定位。
3. 日志只要确认了「内核好的、应用没起」，就说明 B 或 C 只有一条路可走，别再折腾。

---

## 4. 路线 B：NAND 编程器（A 失败时）

### 4.1 要买/要借

| 物品 | 规格 | 参考价 |
|---|---|---|
| NAND 编程器 | **RT809H**（或 XGecu T48/T56，必须支持 TSOP48 NAND） | ¥300–600 |
| TSOP48 转接座 | 0.5mm 间距，48 脚 | ¥30–60 |
| 热风枪 | 858D 之类 | ¥150–250 |
| 吸锡带 / 助焊剂 / 洗板水 | 2mm 吸锡带 | ¥30 |

**注意**：TSOP48 SLC NAND（照片里能看到芯片下边一排引脚，BGA 不会有），不需要植球，
但 48 脚拆焊/回焊需要热风枪手感。

> **关于"免拆夹子读取"——我 2026-11-13 说过这句话，现在收回。**
> 当时的原话是"引脚外露，可以免拆读取，DIY 完全可行"（旧会话 Turn 180）。这是过度乐观：
> 1. 0.5mm 间距 48 脚，夹子要同时压准，板上元件非常密，多数机器上根本没有下夹子的空间；
> 2. NAND 的 CE/RE/WE/ALE/CLE 由 SoC 驱动，断电时 SoC 引脚不是可靠高阻，
>    编程器给芯片供电会经 SoC 的 ESD 二极管倒灌，读数不稳定甚至伤芯片；
> 3. 真要在线读，得先把 SoC 的 nRST 拉低（还得先找到复位点）；
> 4. 我们的目标是"改一个字节再写回"，读出来有一次位翻转就可能毁掉逐机校准数据。
>
> 所以编程器这条路，现实里就是**拆焊**（热风枪），不是夹子。
> 没做过的话，这一步交给维修店做，你只负责给他们 4.3 的参数。

### 4.2 流程（顺序不能变）

1. **完整读两遍，CRC 必须一致**；存成两份不同文件名。
2. 离线验证：`0x420000` 处应是 vfat 引导扇区（见 1.4 的注）。
3. 用仓库脚本打补丁（只动需要的字节）：

```bat
python nex7\hack\setting_patch.py --in dump1.bin --out dump_fixed.bin --oob 64
```

   - `--oob 64`：编程器输出是「每页 2048 数据 + 64 字节 spare」连排时用；
     纯数据镜像（无 spare）写 `--oob 0`。
   - 脚本会打印改了哪几个页/块，并写 `report.txt`。
4. 写回**只写被改动的块**（脚本会告诉你块号），其余块一个字节别碰。
   只能整片写的话也行，但写回后必须读回比对。
5. **ECC 是这条路唯一的坑**：改的是用户数据页，页里的 ECC 是给原始数据算的。
   - 编程器写回时若按芯片型号重算 spare/ECC → 没问题；
   - 只是把读出的 spare 原样写回 → 这一页 ECC 校验失败，vfat 可能读不出来。
   - **问店里一句话**：「写回 NAND 时会不会重算 ECC？」答不上来就退回 A 或 C。
   - 保命条款：**原片 dump 留两份**，写错原样写回就回到今天的状态（完全可回滚）。

### 4.3 给操作者的精确参数

| 项 | 值 |
|---|---|
| 芯片 | Toshiba TC58NVG0S3ETA00，TSOP48，128MiB |
| 页 / OOB | 2048 + 64 字节 |
| 擦除块 | 128KB（0x20000），共 1024 块 |
| **要改的区域** | `/setting` = 偏移 `0x420000`，长 `0x280000`（2.5MB），块 33–52 |
| 唯一要改的内容 | `dmode`：1 字节 `0x78`('x') → `0x33`('3')，目录项长度改 2，写入 `33 0A` |
| 顺带 | `env.txt`、`ldtest.so` 两个目录项首字节改 `0xE5`（=删除）并释放簇链 |
| **绝对不要动** | 块 0（引导区）、nflasha3（/system）、nflasha8（/usr） |

> 手工改也行，但务必只改这一处；用脚本改可以避免手抖（脚本自带 selftest）。

---

## 5. 路线 C：送修

1. 把 `nex7/hack/REPAIR_NEX7.md` 发给店里（一页纸：现象、根因、只改 1 个字节、不要换主板）。
2. 先说清楚：**不要重刷固件**（固件本身是好的，重刷有可能进不去升级模式，反而更糟）。
3. 如果店里说「只能换主板」：NEX-7 主板淘宝约 ¥300–600，换板可行，
   但新板子要重新做实验（每台机器的 /setting 不一样）。
4. 拿回相机后立刻按第 7 节验收。

---

## 6. 工具清单总表（按购买优先级）

### 必买（¥60–120）
- JIS #00 / #000 精密螺丝刀
- 塑料撬棒、尖头镊子
- 防静电手环
- 磁性螺丝垫

### UART 套件（¥100–200）
- 3.3V USB-TTL（CH340/CP2102）
- 细烙铁 + 0.3mm 焊锡 + 助焊剂
- 0.1–0.2mm 漆包线、Kapton 胶带
- 万用表

### 编程器套件（¥500–900，A 失败再买）
- RT809H + TSOP48 转接座
- 热风枪、吸锡带、洗板水

### 软件
- CH340 驱动、PuTTY / Tera Term
- Python 3.12：`C:/Users/<user>/AppData/Local/Programs/Python/Python312/python.exe`
- 本仓库工具：`nex7/hack/setting_patch.py`、`nex7/hack/fw_build.py`、`pmca-console.py`

---

## 7. 修好之后的验收清单

按顺序确认，任何一步不过就停：

1. [ ] 开机有画面、有灯、能进菜单
2. [ ] 插 USB 电脑能识别（海量存储，PID 0x54C/0x57C）
3. [ ] 拍一张 JPEG 能回放（确认 /setting 的逐机数据还在）
4. [ ] 能进升级模式（`python pmca-console.py updatershell -m NEX-7 -d native` 能拿到 `>` 提示符）
5. [ ] 先刷恢复包 `nex7/out_stock99/firmware_packed.dat`，确认版本变 9.99 且一切正常
6. [ ] 只读验证：push 小文件 → shell 里 `ls /tmp` → pull 回来
7. [ ] 最后才评估刷 JPEG 补丁（`out_jpeg_v2`）

## 8. 这次的教训（下次动手前必读）

1. **别碰 init 早期路径**（dmode、env.txt、LD_PRELOAD）——错了就是黑屏，只能拆机。
   运行时注入（scenario 插件、libpro 工厂插件、应用配置文件）才是低风险入口。
2. 任何写 `/setting` 的操作，先 `cp` 到 `/tmp` 并 pull 回电脑。
3. 刷机/改文件前先确认「能进升级模式」，这是唯一的软件后门；进不去就只剩拆机。
4. 一次只改一个变量，改完立刻重启验证。
