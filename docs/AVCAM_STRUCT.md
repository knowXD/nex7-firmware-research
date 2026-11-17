# av-cam.bin 结构初探

## 头部（0x00-0x2F）

- 0x00: `28 F0 8F E2`  add pc, pc, #0x28  -> 跳到 0x30
- 0x04: "ORIL"（魔术字）
- 0x08: 版本 4
- 0x0C-0x2C: 9 个指针（0xC3421050、0xC3421078、0xC3873464 ...）
- 0x30: 入口代码

入口：

- ldr r0, =0xFFF07D00; strb 0xFF, [r0+0x21]
- ldr r0, =0xFFFF0000; bx r0

## RTOS 识别

- uITRON 风格 API：act_tsk、mbf（消息缓冲）、Sem、Flg、Cyc
- OSAL 抽象层字符串约 100 次
- 字符串示例（0x1080 起）：
  - TskAvifVSync
  - VSyncFunc over V border
  - Unable send mbf TskAvifVsync->ID=%d osRet=%d
  - [CDIAG][TSK]act_tsk

## 代码形态

- 入口是 ARM；大量模块是 Thumb 代码（adr 相对寻址）；
- 例：0xF54 处 adr r2, 0x128 -> 0x1080 的字串，
  这是 RTOS 日志/诊断函数的入口区域。

## 已知模块偏移

| 偏移 | 模块 |
|---|---|
| 0x31E390 | Creative Style 名称/ID 映射 |
| 0x2B7A10 | MP4 码率常量表 |
| 0x461092 | JPEG 量化表 |
| 0x44CFF0 | 内存拷贝/填充 |
| 0x250578 | 通用参数设置 |

## 后续方向

1. RTOS 系统调用表（act_tsk/mbf 分发入口）；
2. 按字符串簇划分模块边界；
3. 消息队列/邮箱使用图，理解模块间数据流。
## 追加：LIRO 与加载器（im.elf）

- av-cam 头部魔术字字节为 "ORIL"，按小端解释是 **0x4C49524F = "LIRO"**，
  即索尼自研 RTOS 的名字；
- 加载器是 `/bin/im.elf`（IM core），相关字符串：
  - `IMc: %s: trying BKID_RAM_ADDR_GP_LIRO`
  - `IMc: %s: liro_addr=0x%x, err:%d`
  - `fn=/system/av-cam.bin load=1 debug=1`
  - `__u_IMCORE_liro_ko_init`
  - `init_module: failed(%d)`
- 结论：av-cam 的装载地址由板级 ID（BKID_RAM_ADDR_GP_LIRO）在运行时决定，
  不是固定基址；因此文件里指针分布跨度很大（0xC3000000-0xC3B00000）。
- 下一步可从这个 BKID 值或启动日志（liro_addr=0x...）确认实际地址。
## LIRO 的真实形态（重要）

LIRO 不是裸机 RTOS，而是**以 Linux 内核模块形式实现**：

- `initrd/kmod/liro.ko`（69,816 字节）实现了完整的 µITRON API；
- 符号表完整：CRE_TSK/cre_tsk/tsk_entry、CRE_SEM/sig_sem、
  CRE_MBX/trcv_mbx、cre_mbf/tsnd_mbf/trcv_mbf、cre_cyc、cre_alm、
  os_request_irq/def_inh、liro_init/liro_proc_init 等；
- RTOS 任务以 Linux kthread 形式存在（tsk_thread_helper、os_thread_bind），
  由 LIRO 自己的调度钩子（ltron_sched_hook）管理；
- 驱动暴露 `/proc/liro/start`，写入后启动 LIRO；
  日志里还有 "Address not set, firmware will no be loaded!"，
  说明启动时需要传入 av-cam 的装载地址（adrs=%08x）。

## 调试模式（change_mode.sh）

- 0：只启动内核
- 1：+ 全局基础设施
- 2：+ LIRO（不启动 appFw）
- 3：+ appFw（默认）
- 3L/3w/3k/3g/3s/3d/3e：LeakTracer / WCheck / KMC ICE / target gdb /
  gdbserver / DUMA / eFence

注意：**gdb/gdbserver 在 NEX-7 上不可用**。核实结果：
- 内核没有网络栈（net_device/sk_buff/tcp/rndis/usbnet 符号均为 0）；
- /usr 里没有 gdb/gdbserver 可执行文件；
- 因此 bootin.elf 里的 "gdbserver 0.0.0.0:10000" 是通用平台代码，
  在本机型上是死代码，执行会失败。
可用的本地调试辅助：LeakCheck(LeakTracer)、appdbglv.sh、mpr_monio.elf、
mpr_viewLog.elf、msdump.elf 等。
## liro.ko 的接口细节

- 符号：liro_init、liro_proc_init、proc_suspend、proc_delay_write、
  liro_resume、liro_suspend、tsk_thread_helper、ltron_sched_hook；
- 字符串：/proc/liro/start、"Address not set, firmware will no be loaded!"、
  "Param:adrs=%08x, debug=%d, delay=%d"；
- 结论：av-cam 的装载地址通过 /proc/liro/start 写入触发，
  未设置地址时固件不会被加载；
- liro.ko 是 ET_REL（可重定位目标），.text 在文件 0x58，
  .rel.text 在 0xdc30；静态反汇编需要先应用重定位。
## 装载参数（liro.ko .rodata）

模块参数名：`adr`、`load`、`debug`、`delay`（另有 alba、resume_cpu、liro_resume_async）。

装载链：

1. im.elf 通过 BKID 接口读取 BKID_RAM_ADDR_GP_LIRO；
2. 以模块参数 `adr=0x... load=1 debug=1` 加载 liro.ko；
3. liro.ko 把 /system/av-cam.bin 复制/加载到 adr 指定的地址；
4. 写 /proc/liro/start 触发 LIRO 启动。

## 反汇编方法（可复用）

`r2 -2 -e bin.relocs.apply=true` 可以直接解析 liro.ko 的重定位，
调用目标会显示为 reloc.printk / reloc.proc_mkdir 等符号名。
## 模块地图（按源文件名聚类，约 400 个源文件）

| 模块组 | 文件数 |
|---|---|
| 其他（框架/工具） | 146 |
| 对焦控制 FC/* | 66 |
| AVC 编解码 | 51 |
| JPEG 编解码（dgi_jpeg_*） | 32 |
| 编码控制状态机 CdcMgr* | 22 |
| Stage_* | 16 |
| Media Core mc* | 14 |
| 拍摄流程 Capture*/capcon | 13 |
| 同步/时钟 Sync/* | 11 |
| Resize/Copy Rc* | 11 |
| SDF 任务 tsk_sdf_* | 7 |
| SDF 调试 | 6 |
| 子系统框架 Subsystem* | 3 |
| EXIF | 2 |
| Function 层 | 2 |
| Imaging | 1 |

### 与画质/码率直接相关的模块

- JPEG：src/dgi_jpeg_encode.c、dgi_jpeg_qtable.c、dgi_jpeg_fast_enc.c、
  dgi_jpeg_estimate.c、dgi_jpeg_tanz_*.c、tsk_sdf_jpegsort.cpp；
- 码率：src/RcDriver.cpp、CdcMgrEncSeq*（Open/Start/Stop/NextFrame 状态机）、
  avcEncVideoCtrlIf.cpp；
- 色彩：未在此列表中出现独立 ISP 模块，风格处理可能在 tsk_sdf_* 或 其他组。

### 分析难点

0x461000 附近是代码与数据表混排区域（量化表、跳转表、字符串交错），
线性反汇编会产生误判（例如把数据表当成跳转目标）。需要按 xref 精确定位函数入口。