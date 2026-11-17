# 相机复活后的 90 分钟行动清单

> 写给"那一天的自己"看：手会抖、脑子会热，最容易犯的错是**顺手多改一个东西**。
> 全程只有 **一次写操作**（改 dmode），其余都是只读。

---

## 0. 三条红线（动手前读一遍）

1. **先备份，再改**。哪怕只改一个字节，也要先把 /setting 拉回电脑。
2. **一次只改一个东西**，改完立刻重启验证。不要"顺便把 env.txt 也删了、顺便把版本也改了"。
3. **复活当天不刷任何补丁包**。哪怕 out_stock99 再稳，也等这一步彻底验收完，隔一天再说。

---

## 1. T+0 ～ 10 分钟：接通串口

### 接线检查（不插电先看）
- [ ] 模块 TXD 空闲电压已量过，是 **3.3V**（不是 5V）
- [ ] 只接了两根：**GND ↔ GND**、**模块 RXD ↔ 相机 TX**
- [ ] **VCC 没接**
- [ ] 模块插电脑，"设备管理器"里出现 COM 口
- [ ] 电池满电

### 抓日志
串口终端 115200 8N1，**流控 None**，打开 COM 口 → 装电池 → 开机（拨杆保持 ON）。

| 看到什么 | 说明 | 下一步 |
|---|---|---|
| 成规律乱码 | 波特率不对 | 依次试 **38400 / 9600 / 57600** |
| 完全没字符 | 接触不良或 TX 点不对 | 先动线、压紧探针，再换点 |
| 内核日志（init/insmod/<<init start>>） | 通了 | 等它跑完 |
| `/ #` 或 `#` 提示符 | **拿到 root shell** | 跳到第 2 节 |

> 10 分钟还没出日志：别硬扛，拍照发我，先判断是"点不对"还是"线没通"。

---

## 2. T+10 ～ 20 分钟：只读侦察（一个字都不写）

```sh
mount | head -20                 # 确认 /setting、/system、/usr 挂上了
cat /proc/partitions             # 分区有没有认全
cat /setting/mode/dmode ; echo   # 现在应该是 x
cat /setting/env.txt             # 应该是 LD_PRELOAD=/setting/ldtest.so
ls -la /setting                  # 核对文件清单（应有 .hasp/Backup.bin/DmmConfig.bin…）
uname -a                         # 内核版本（2.6.29 那条）
```

**拍下屏幕 / 复制粘贴这些输出**。这一步是"取证"，是之后判断"改动前后有没有差别"的基准。

> 如果 `/setting` 没挂上：先跑 `dosfsck -Y /dev/nflasha2` 再 `mount -t vfat /dev/nflasha2 /setting`。

---

## 3. T+20 ～ 30 分钟：唯一的写操作

```sh
echo 3 > /setting/mode/dmode     # 产生 "3\n"，和官方 change_mode.sh 写法一致
cat /setting/mode/dmode ; echo   # 必须看到 3
rm -f /setting/env.txt           # 不删的话，ldtest.so 会被预加载进 sen.elf
rm -f /setting/ldtest.so
sync
```

**确认三件事再重启**：dmode 是 3、env.txt 没了、sync 过了。

```sh
reboot
```

---

## 4. T+30 ～ 60 分钟：开机验证 + 立刻备份

### 验证（屏幕上）
- [ ] 有画面、有灯、能进菜单
- [ ] 拍一张 JPEG，回放正常（说明 /setting 的逐机数据没坏）
- [ ] 插 USB，电脑识别成相机（这是"用户态活了"的铁证）

### 备份（USB 能用了，或还在串口 shell 里）
优先用升级模式的 shell 拉：

```bat
python pmca-console.py updatershell -m NEX-7 -d native
> tar cf /tmp/setting.tar /setting
> pull /tmp/setting.tar nex7/backup_setting_<日期>.tar
> exit
```

**这份 backup 存两个地方。** 以后再动 /setting 之前，先确认它还在。

---

## 5. T+60 ～ 90 分钟：确认"后路还在"

- [ ] 能进升级模式（updatershell 拿到 `>` 提示符）
- [ ] `info` 显示 固件 1.03、型号 NEX-7
- [ ] （可选）dump 一份 NAND：`nandump2 2 /tmp/s2.bin` + `pull`，然后本地跑
      `python nex7/hack/dump_check.py --in s2.bin --oob 64` 验证

> 拿到 dump 就等于拿到了"后悔药"：以后任何 NAND 级操作都能回滚。

---

## 6. 如果串口只有日志、没有 shell

说明 `/dev/ttyAM0` 被别的东西占着或 init 没走到 shell_loop。此时：

1. 先看日志里有没有 `shell_loop: can not open /dev/ttycons` —— 有就是节点问题；
2. 没有的话，**改走编程器路线**（[REPAIR_NEX7.md](REPAIR_NEX7.md) + `setting_patch.py`）；
3. 不要把相机再拆更散——拆得越多，回装风险越大。

---

## 7. 出岔子了怎么办

| 现象 | 判断 | 动作 |
|---|---|---|
| 改完重启黑屏 | dmode 写坏了 | 串口还在就再改一次；不在就备份包/编程器 |
| 串口突然没输出 | 线松了 | 先查线，再查电量 |
| 相机无限重启 | /setting 挂载失败 | 串口里 `dosfsck -Y /dev/nflasha2` |
| 能开机但 USB 不识别 | 用户态部分起不来 | 串口看 sen.elf 有没有报错 |
| 焊点被拉掉 | 板子受伤 | 停手，拍照发我 |

---

## 8. 当天禁止做

1. 刷任何功能补丁包（stock99 / jpeg_v2 / delegate 都不行）
2. 改 /system、/usr（那是另一层，复活当天不碰）
3. 用 `bootloader` / `bootrom` 命令（会卡死 USB 端点，要拔电池）
4. 在没有备份的情况下删 /setting 里任何文件

---

## 9. 记录模板（做完填，方便复盘）

| 时间 | 操作 | 结果 | 证据（截图/日志名） |
|---|---|---|---|
| T+05 | 115200 打开 | 满屏乱码 | — |
| T+07 | 38400 重开 | 看到 init 日志 | 截图 1 |
| … | … | … | … |
