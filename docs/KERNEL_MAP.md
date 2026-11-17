# NEX-7 内核子系统地图（基于 kallsyms）

## 平台层

- CXD4132：map_io、init_irq、core_init、时钟表、CPUID、xrstreq
- CXD4115：timer、PM、SMP secondary entry、head_init
- GPIO / 设备接口：udif（gpio_open/suspend/resume 等）
- watchdog：watchdog_touch / watchdog_tick

## 存储与文件系统

- 块层：blkdev_*、gendisk
- nand：仅 nand_init / nand_exit（很精简）
- 文件系统：cramfs（含 LZ77 解压）、fat、axfs（另一种压缩只读 FS）
- 页大小 4096 → cramfs 块 4096，与 TPZL 分段一致

## USB

- 索尼自定义栈：usb_scd_*、usb_otgcore_*、usb_gcore_*、usb_gcw_*、usb_event_*
- 内核里没有 mass storage class 驱动
- 升级模式（0x3E2）由引导程序/升级 body 负责，不在 Linux 内核里

## 媒体相关

- 搜不到 dsp / codec / pcm / i2s / jpeg / hdmi / isp / sensor 符号
- 说明图像处理、编码、音频全部在 av-cam.bin（µITRON）和 /usr 应用层，
  内核只做平台初始化和 USB/存储

## 对后续工作的意义

1. JPEG 质量、码率、色彩：目标在 av-cam，不在内核；
2. 变砖恢复：升级模式在 Linux 之下，内核分析帮不上；
3. 镜像重打包：内核提供 cramfs-LZ77 与 FAT 的权威实现，可对照。
