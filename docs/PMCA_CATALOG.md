# PMCA 应用全表与"原生复刻"评估（2026-11-15 归档）

> 来源：用户从另一个对话（2026-10-23 17:38）贴过来的分析，已归档。
> 下面 [复核] 是我 2026-11-15 的补充。

## 一、官方应用（约 24 款 + 4 款 BETA）

| 应用 | 功能 | 需 Wi-Fi | 对 NEX-7 的意义 |
|---|---|---|---|
| Bracket Pro | 一次拍多张不同快门/光圈 | 否 | 可原生复刻 |
| Multi-shot NR | 连拍对齐合成降噪 | 否 | 机内合成难 |
| Time-lapse | 间隔拍摄合成延时 | 否 | 最容易复刻 |
| Multiple Exposure | 机内多重曝光 | 否 | 可复刻 |
| Motion Shot | 运动轨迹合成 | 否 | 需机内合成 |
| Light Shaft | 光束效果 | 否 | 后期更好 |
| Star Trail | 星轨（Motion JPEG） | 否 | 需堆栈 |
| Smooth Reflection | 模拟 ND 长曝 | 否 | 需堆栈 |
| Sky HDR | 天空 HDR 替换 | 否 | 需合成 |
| Light Trail | 光轨 | 否 | 需合成 |
| Touchless Shutter | 挥手触发快门 | 否 | NEX-7 有 EVF 传感器 |
| Stop Motion | 定格动画 | 否 | 可复刻 |
| Picture Effect+ | 6 种滤镜 | 否 | 后期更好 |
| Liveview Grading | 视频实时调色 | 否 | 需改视频管线 |
| Lens Compensation | 像差补偿 | 否 | 设置层 |
| Snapshot me / Photo Retouch / Catch Light / ID Photo / Cinematic Photo / Sound Photo | 各类小工具 | 否 | 意义不大 |
| Smart Remote / Direct Upload / Smartphone Sync | 遥控、直传 | **是** | NEX-7 无 Wi-Fi |

两个事实：**app 有按机型的白名单**；**app 是 SPK 包（APK+manifest+签名），由 ScalarAInstaller 装**。

## 二、复核（2026-11-15）

1. **"只要 root + 自启就够"——这句要打折。**
   我们连"自启"都还没验证：`/setting/env.txt` + `dmode` 那次注入正是变砖的原因。
   入口机制本身是未证明状态。

2. **6 个功能要分成两类，不能混在一起排优先级：**

   | 类别 | 例子 | 需要的底层能力 | 难度 |
   |---|---|---|---|
   | A 类：只要"触发一次拍照" | Time-lapse、Bracket | 发一条 capture trigger 消息 | 中 |
   | B 类：需要"拿到多帧原始数据" | Multi-shot NR、Star Trail、Light Trail、Smooth Reflection | ISP/编码器的帧缓冲访问 | 高一个量级 |

   B 类不是"触发快门"能解决的——它要求机内拿到连续帧再合成，而帧缓冲在 ISP 里，我们没有接口。

3. **A 类有希望**：在 `libObj.so` 里能找到
   `PARAMID_CAPTURE_START_TRIGGER`、`PARAMID_CAPTURE_ID`、`MSGID_SET_DUALREC_CAPTURE_EXPAND_MODE_CMD`、
   `model/STILL_REC`、`MID_SET_STILL_MONITORING_FORMAT_COMP` ——
   说明**拍照是消息驱动**的，理论上插件能发。

   真正要查的是：这条消息的**结构 + 目标进程 + 插件能否到达**。

## 三、下一步（离线可做）

反推 `PARAMID_CAPTURE_START_TRIGGER` 的消息格式（在 `libObj.so` 里找它的调用点与结构体），
这决定 A 类两个功能能不能做。B 类先不碰。
