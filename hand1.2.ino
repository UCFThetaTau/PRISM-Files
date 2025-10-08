#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pwm(0x40);

// ====== TUNE THESE FOR YOUR SERVO MODEL ======
const int   SERVO_FREQ     = 50;     // 50 Hz for hobby servos
int         SERVO_MIN_US   = 600;    // pulse at 0°   (try 500–700)
int         SERVO_MAX_US   = 2400;   // pulse at max° (try 2300–2500)
int         SERVO_MAX_DEG  = 270;    // set 180 or 270 depending on servo
// =============================================

static float currentAngle[16];   // live (what we’re outputting now)
static float targetAngle[16];    // where we want to go
static float speedDps[16];       // degrees per second
int currentChannel = 0;

int clampi(int v, int lo, int hi) { return v < lo ? lo : (v > hi ? hi : v); }
float clampf(float v, float lo, float hi){ return v < lo ? lo : (v > hi ? hi : v); }

int angleToMicros(float angle) {
  angle = clampf(angle, 0, SERVO_MAX_DEG);
  long us = map((long)(angle * 1000), 0, SERVO_MAX_DEG * 1000L, SERVO_MIN_US, SERVO_MAX_US);
  return (int)us;
}

void writeAngle(uint8_t ch, float angle) {
  ch = clampi(ch, 0, 15);
  pwm.writeMicroseconds(ch, angleToMicros(angle));
}

void printHelp() {
  Serial.println();
  Serial.println(F("Commands:"));
  Serial.println(F("  h              : help"));
  Serial.println(F("  c <ch>         : select current channel (0-15)"));
  Serial.println(F("  a <angle>      : set target angle for current channel (0..SERVO_MAX_DEG)"));
  Serial.println(F("  s <speed>      : set speed for current channel (deg/sec, e.g. 60)"));
  Serial.println(F("  <ch> <angle>   : set target for a specific channel (keeps its speed)"));
  Serial.println(F("  test           : sweep current channel"));
  Serial.print (F("  Current ch: ")); Serial.println(currentChannel);
  Serial.print (F("  SERVO_MAX_DEG=")); Serial.println(SERVO_MAX_DEG);
  Serial.print (F("> "));
}

void setup() {
  Serial.begin(115200);
  while(!Serial){;}
  Serial.println(F("\n[PCA9685] Smooth ramp controller"));

  // If you’re on ESP32/ESP8266, set pins before begin:
  // Wire.begin(21,22); // ESP32
  // Wire.begin(4,5);   // ESP8266

  pwm.begin();
  pwm.setOscillatorFrequency(27000000); // helps some clones
  pwm.setPWMFreq(SERVO_FREQ);

  // Defaults
  for (int i=0;i<16;i++) {
    currentAngle[i] = 0;
    targetAngle[i]  = 0;
    speedDps[i]     = 60;  // 60°/s default speed
    writeAngle(i, currentAngle[i]);
  }
  printHelp();
}

unsigned long lastUpdateMs = 0;

void rampUpdate() {
  // Run at ~100 Hz
  unsigned long now = millis();
  if (now - lastUpdateMs < 10) return;
  float dt = (now - lastUpdateMs) / 1000.0f;
  lastUpdateMs = now;

  for (int ch=0; ch<16; ch++) {
    float cur = currentAngle[ch];
    float tgt = clampf(targetAngle[ch], 0, SERVO_MAX_DEG);
    float s   = speedDps[ch];
    if (s <= 0) continue;

    float step = s * dt;              // how many degrees to move this tick
    if (fabs(tgt - cur) <= step) {
      currentAngle[ch] = tgt;
    } else if (tgt > cur) {
      currentAngle[ch] = cur + step;
    } else {
      currentAngle[ch] = cur - step;
    }
    writeAngle(ch, currentAngle[ch]);
  }
}

void doTestSweep(int ch) {
  Serial.println(F("[TEST] Sweep current channel"));
  targetAngle[ch] = 0;    delay(1000);
  targetAngle[ch] = SERVO_MAX_DEG;    delay(2000);
  targetAngle[ch] = SERVO_MAX_DEG/2;  delay(1500);
  Serial.println(F("[TEST] Done."));
}

void loop() {
  rampUpdate();

  if (!Serial.available()) return;

  String line = Serial.readStringUntil('\n');
  line.trim();
  if (line.length()==0) { Serial.print("> "); return; }

  if (line == "h" || line == "H") { printHelp(); return; }
  if (line == "test") { doTestSweep(currentChannel); Serial.print("> "); return; }

  if (line.startsWith("c ")) {
    int ch; if (sscanf(line.c_str(), "c %d", &ch) == 1) {
      currentChannel = clampi(ch, 0, 15);
      Serial.print(F("Current channel = ")); Serial.println(currentChannel);
    }
    Serial.print("> "); return;
  }

  if (line.startsWith("a ")) {
    float ang; if (sscanf(line.c_str(), "a %f", &ang) == 1) {
      targetAngle[currentChannel] = clampf(ang, 0, SERVO_MAX_DEG);
      Serial.print(F("CH ")); Serial.print(currentChannel);
      Serial.print(F(" target -> ")); Serial.print(targetAngle[currentChannel]); Serial.println(F("°"));
    }
    Serial.print("> "); return;
  }

  if (line.startsWith("s ")) {
    float sp; if (sscanf(line.c_str(), "s %f", &sp) == 1) {
      speedDps[currentChannel] = (sp < 0) ? 0 : sp;
      Serial.print(F("CH ")); Serial.print(currentChannel);
      Serial.print(F(" speed -> ")); Serial.print(speedDps[currentChannel]); Serial.println(F(" °/s"));
    }
    Serial.print("> "); return;
  }

  // Try "<ch> <angle>"
  int ch, ang;
  if (sscanf(line.c_str(), "%d %d", &ch, &ang) == 2) {
    ch = clampi(ch, 0, 15);
    targetAngle[ch] = clampf((float)ang, 0, SERVO_MAX_DEG);
    Serial.print(F("CH ")); Serial.print(ch);
    Serial.print(F(" target -> ")); Serial.print(targetAngle[ch]); Serial.println(F("°"));
    Serial.print("> "); return;
  }

  Serial.println(F("[ERR] Unknown command. Type 'h' for help."));
  Serial.print("> ");
}
