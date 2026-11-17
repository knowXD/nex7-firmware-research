# NEX-7 应用层逆向记录

## 进程架构（已确认）

```
init (initrd, AXFS)
  ├─ insmod 驱动（USB、存储、HDMI...）
  ├─ 读取 /setting/mode/dmode → 标志位
  ├─ 读取 /setting/env.txt（仅 oreore 模式）
  ├─ 可选 LD_PRELOAD（kmcsup / eFence / DUMA）
  ├─ run_bg_process(/usr/bin/bootin.elf)
  │     └─ 解析 dmode/cmode，fork im.elf
  │           └─ im.elf: 链接 libObj.so（UI）、libIMDB，
  │              加载 /system/av-cam.bin 到 LIRO
  └─ run_bg_process(/usr/bin/sen.elf)（条件启动）
        └─ 读 /setting/sen/smode → dlopen libsencore.so
             → senser_normal_mode_start / usb_mode_start
             → 加载 libproXX.so 插件（工厂命令）
```

## dmode 标志位（check_mode_file）

| 字符 | 作用 |
|---|---|
| '3' 前缀 | appFw 启动（sen.elf） |
| '0' | 仅内核 |
| 'k' | LD_PRELOAD=/usr/lib/libkmcsup.so.2.0.0 |
| 'g' | GDB 模式（bootin 用 system 启动） |
| 'd' | LD_PRELOAD=/usr/lib/libduma.so + DUMA 环境 |
| 'e' | LD_PRELOAD=/usr/lib/libsonyefence.so |
| 'L' | LeakTracer（bootin 里处理） |

注意：内容不是 '3' 开头时，sen.elf 不启动。

## 扩展点

### 1. 场景插件 /usr/scenario/*.so

- 27 个 .so（AVBB_SCN_* / CAMERA_SCN_* / MPR_SCN_*）；
- scenario.elf 可按名字加载并传 payload；
- 触发方式：命令/事件。

### 2. 传感器插件 libproXX.so

- libsencore.so 的 GetPluginModule / CreatePluginCommand；
- 命名 libpro%02X.so；
- 现有 libpro00.so 实现 command001F / command00F1（HASP 授权）。

### 3. 调试注入

- dmode 选择调试库，init/bootin 设置 LD_PRELOAD；
- 加载发生在 bootin/im/sen 之前，出错会导致应用不启动。

### 4. 配置文件

- /setting/mode/dmode、cmode；
- /setting/env.txt；
- /setting/sen/smode；
- /setting/.hasp、facedmy.bin 等。

## 安全规则（血泪教训）

1. 不碰 init 早期读取的文件（dmode/env.txt）；
2. 任何注入先在 /tmp 验证；
3. 必须有 DISABLE 开关；
4. 写前备份、写后回读、冷启动验证。
