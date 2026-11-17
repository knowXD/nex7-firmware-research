# NAND 备份 / 恢复方案（updater 模式 payload）

## 目标

刷机前把整机 NAND 分区完整备份出来；万一变砖且相机还能进升级模式，
可以用备份写回，不需要 NAND 编程器。

## 原理

- 固件更新包里的 `updater.img` 是相机在升级模式下启动的 initrd；
- 升级模式下，相机以 root 运行 updater body，主机通过 USB 发送命令；
- PMCA-RE 的 `updatershell` 就是利用这个机制拿到一个 shell；
- 因此我们可以把静态 ARM 程序送进相机、在 /tmp 里执行。

## 组成

1. **nandump**（已编译：`nex7/hack/nandump`，静态 ARM，~850KB）
   - 读 `/dev/nflasha1` .. `/dev/nflasha8`；
   - 写到 `/tmp/dump/nflashaN.bin`；
   - 每个分区输出一行 `路径,字节数,CRC32` 清单。

2. **主机侧**：`pmca-console updatershell -d native`

## 使用步骤

1. 相机进入升级模式（能正常开机时，用 firmware 流程切换；或直接 updatershell）；
2. 在 shell 中执行：
   - 上传：`push nex7/hack/nandump /tmp/nandump`
     （若 shell 无 push，可用 base64 分块写入）
   - `chmod +x /tmp/nandump`
   - `/tmp/nandump /tmp/dump`
3. 把 dump 取回电脑：`pull /tmp/dump/nflasha3.bin nex7/dump/`
   （或先 `tar cf /tmp/dump.tar /tmp/dump` 再 pull，减少往返）；
4. 保存好输出的 CRC 清单，恢复前先比对。

## 恢复

待写 `nandrestore`：读入 dump 文件，校验大小与 CRC，写回对应 `/dev/nflashaN`。
写回前必须确认分区大小一致，避免写坏。

## 限制

- 需要相机能进升级模式；`/system` 损坏且无法进升级模式的机器救不了；
- 不能验证 bootloader 是否接受新的 `/system`（那是启动阶段的行为）；
- 备份文件较大（整机约 100MB+），需要足够空间。

## 下一步

1. 写 `nandrestore`；
2. 把 `nandump` 打进 updater.img，并在 `startupdate.sh` 开头自动执行，
   实现“一插即备份”；
3. 备份完成后再继续正常更新流程。
## 实测记录（2026-11-12，NEX-7 新主板）

- 序列号 756837，固件 1.03，Backup 区域 CX75601_CN2；
- `updatershell -m NEX-7` 可用（payload 在 updatershell/fdat/CXD4132/NEX-7.hdr）；
- 模式切换有时需要 30–60 秒，工具默认 30 秒会超时；已把等待上限改成 120 秒；
- 平台 shell 命令：help/exit/info/shell/push/pull/bootloader/bootrom/install/tweak/bk*；
- **bootrom 和 bootloader 命令在 NEX-7 上报错**
  （DeviceIoControl 31，设备无响应），并把 USB 端点卡死：
  相机停留在升级模式、屏幕黑、存取灯常亮、拨杆关不掉，只能拔电池。
- 结论：不要再用 bootrom/bootloader；NAND 备份应走 `shell` + `dd`，
  先从小分区开始试，确认 shell 可用再继续。
