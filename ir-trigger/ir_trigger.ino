/*
 * Sony SIRC 红外间隔触发器（ESP32 / Arduino 通用）
 * ------------------------------------------------------------
 * 功能：
 *   - 立即快门      0x2D
 *   - 2 秒延迟快门  0x37（让相机先对焦）
 *   - 录像启停      0x48
 *   - 间隔拍摄：每 N 秒发一次快门，可设张数
 *
 * 协议（Sony SIRC，20 bit = 7 位命令 + 13 位地址）：
 *   载波 40kHz，占空比 ~25%
 *   起始：2400us 载波 + 600us 间隔
 *   逻辑0：600us 载波 + 600us 间隔
 *   逻辑1：1200us 载波 + 600us 间隔
 *   顺序：先 7 位命令（高位在前），再 13 位地址（高位在前）
 *   NEX/Alpha 通用地址：0x1E3A
 *
 * 接线（必须用三极管，GPIO 直接推不动红外 LED）：
 *   GPIO4 ──1kΩ── S8050 基极
 *   5V ── LED正极 ── 100Ω ── 集电极
 *   发射极 ── GND
 *
 * 串口（115200）命令：
 *   s            立即快门
 *   d            2 秒延迟快门
 *   v            录像启停
 *   i <秒> <张数> 开始间隔拍摄（张数 0 = 无限）
 *   x            停止间隔
 *   ?            帮助
 */

#include <Arduino.h>

// ---------------- 可改的配置 ----------------
#define IR_PIN        4        // 红外 LED 驱动脚
#define STATUS_LED    2        // ESP32 板载蓝灯
#define CARRIER_HZ    40000
#define LEDC_CH       0
#define LEDC_BITS     8

static const uint16_t SIRC_ADDR   = 0x1E3A;
static const uint8_t  CMD_SHUTTER = 0x2D;
static const uint8_t  CMD_2SEC    = 0x37;
static const uint8_t  CMD_VIDEO   = 0x48;
// -------------------------------------------

static bool          intervalRunning = false;
static unsigned long intervalMs      = 0;
static long          shotsLeft       = 0;      // <0 表示无限
static unsigned long nextShotAt      = 0;

// --- 红外载波开关 ---
static inline void carrierOn()  { ledcWrite(LEDC_CH, 64); }   // 64/255 ≈ 25%
static inline void carrierOff() { ledcWrite(LEDC_CH, 0);  }

static inline void mark(uint16_t us)  { carrierOn(); delayMicroseconds(us); carrierOff(); }
static inline void space(uint16_t us) { delayMicroseconds(us); }

// --- 发一帧 SIRC ---
static void sendSircFrame(uint8_t cmd, uint16_t addr) {
  mark(2400); space(600);                 // 起始位
  for (int8_t i = 6; i >= 0; i--) {       // 7 位命令，高位先发
    bool one = (cmd >> i) & 1;
    mark(one ? 1200 : 600); space(600);
  }
  for (int8_t i = 12; i >= 0; i--) {      // 13 位地址，高位先发
    bool one = (addr >> i) & 1;
    mark(one ? 1200 : 600); space(600);
  }
}

// --- 发一条命令（SIRC 惯例：连发 3 帧） ---
static void sendCommand(uint8_t cmd) {
  for (uint8_t r = 0; r < 3; r++) {
    sendSircFrame(cmd, SIRC_ADDR);
    delay(25);
  }
  digitalWrite(STATUS_LED, HIGH);
  delay(15);
  digitalWrite(STATUS_LED, LOW);
}

static void printHelp() {
  Serial.println();
  Serial.println("=== Sony SIRC 红外间隔触发器 ===");
  Serial.println("  s            立即快门 (0x2D)");
  Serial.println("  d            2 秒延迟快门 (0x37)");
  Serial.println("  v            录像启停 (0x48)");
  Serial.println("  i <秒> <张数> 间隔拍摄，张数 0 = 无限");
  Serial.println("  x            停止间隔");
  Serial.println("  ?            显示帮助");
  Serial.println("地址 0x1E3A / NEX 与 Alpha 通用");
  Serial.println();
}

static void startInterval(unsigned long sec, long count) {
  if (sec < 1) sec = 1;
  intervalMs      = sec * 1000UL;
  shotsLeft       = (count <= 0) ? -1 : count;
  nextShotAt      = millis() + intervalMs;
  intervalRunning = true;
  Serial.printf("[间隔] 每 %lu 秒一张，共 %ld 张（-1=无限）\n", sec, shotsLeft);
}

static void stopInterval() {
  intervalRunning = false;
  Serial.println("[间隔] 已停止");
}

void setup() {
  pinMode(STATUS_LED, OUTPUT);
  digitalWrite(STATUS_LED, LOW);

  ledcSetup(LEDC_CH, CARRIER_HZ, LEDC_BITS);
  ledcAttachPin(IR_PIN, LEDC_CH);
  ledcWrite(LEDC_CH, 0);

  Serial.begin(115200);
  delay(300);
  printHelp();
}

void loop() {
  // ---- 串口命令 ----
  if (Serial.available()) {
    String line = Serial.readStringUntil('\n');
    line.trim();
    if (line.length() == 0) {
      // 忽略空行
    } else if (line == "s") {
      Serial.println("[命令] 快门");
      sendCommand(CMD_SHUTTER);
    } else if (line == "d") {
      Serial.println("[命令] 2 秒延迟快门");
      sendCommand(CMD_2SEC);
    } else if (line == "v") {
      Serial.println("[命令] 录像启停");
      sendCommand(CMD_VIDEO);
    } else if (line == "x") {
      stopInterval();
    } else if (line == "?") {
      printHelp();
    } else if (line.startsWith("i ")) {
      unsigned long sec = 0;
      long count = 0;
      int n = sscanf(line.c_str() + 2, "%lu %ld", &sec, &count);
      if (n >= 1) {
        if (n == 1) count = 0;          // 只给秒数 = 无限
        startInterval(sec, count);
      } else {
        Serial.println("[错误] 用法：i <秒> <张数>");
      }
    } else {
      Serial.println("[错误] 未知命令，输入 ? 看帮助");
    }
  }

  // ---- 间隔触发 ----
  if (intervalRunning && (long)(millis() - nextShotAt) >= 0) {
    sendCommand(CMD_SHUTTER);
    if (shotsLeft > 0) {
      shotsLeft--;
      Serial.printf("[间隔] 已拍，剩 %ld 张\n", shotsLeft);
      if (shotsLeft == 0) {
        intervalRunning = false;
        Serial.println("[间隔] 完成");
      }
    } else {
      Serial.println("[间隔] 已拍一张（无限模式）");
    }
    nextShotAt = millis() + intervalMs;
  }
}
