/*
  2023-12 Arduino + Raspberry Pi line tracer, dialogue-based RECONSTRUCTION.
  NOT a recovered historical Arduino sketch. Use only after real hardware checks.

  CONFIRMED from conversation:
    button pin 3 INPUT_PULLUP (pressed means message field 1)
    left motors CW=5 CCW=6; right motors CW=9 CCW=10
    IRL/IRR: HH forward, LH left, HL right, LL stop
    Arduino -> Pi: r:g:b:button followed by LF
    Pi -> Arduino: result 0/1 (0=stop, 1=line-follow)
  ASSUMED: IRL pin2, IRR pin4, baud 9600, motor speeds, RGB conversion,
           timeout durations, button hardware debounce, TCS34725 gain.
*/
#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_TCS34725.h>

const uint8_t BUTTON_PIN = 3;
const uint8_t LmotorCW = 5;
const uint8_t LmotorCCW = 6;
const uint8_t RmotorCW = 9;
const uint8_t RmotorCCW = 10;

// Unverified wiring. Confirm pin assignments against original device.
const uint8_t IRL_PIN = 2;
const uint8_t IRR_PIN = 4;
const unsigned long SERIAL_BAUD = 9600;
const unsigned long RESPONSE_TIMEOUT_MS = 800; // reconstruction: async Pi normally replies quickly
const uint8_t FORWARD_PWM = 150;
const uint8_t TURN_PWM = 135;
const uint8_t IDLE_DELAY_MS = 30;

Adafruit_TCS34725 tcs(TCS34725_INTEGRATIONTIME_50MS, TCS34725_GAIN_4X);

void setLeft(int speed) {
  speed = constrain(speed, -255, 255);
  if (speed >= 0) {
    analogWrite(LmotorCCW, 0);
    analogWrite(LmotorCW, speed);
  } else {
    analogWrite(LmotorCW, 0);
    analogWrite(LmotorCCW, -speed);
  }
}

void setRight(int speed) {
  speed = constrain(speed, -255, 255);
  if (speed >= 0) {
    analogWrite(RmotorCCW, 0);
    analogWrite(RmotorCW, speed);
  } else {
    analogWrite(RmotorCW, 0);
    analogWrite(RmotorCCW, -speed);
  }
}

void stopMotors() {
  setLeft(0);
  setRight(0);
}

void followLine() {
  const int IRL = digitalRead(IRL_PIN);
  const int IRR = digitalRead(IRR_PIN);
  if (IRL == HIGH && IRR == HIGH) {
    setLeft(FORWARD_PWM); setRight(FORWARD_PWM);
  } else if (IRL == LOW && IRR == HIGH) {
    setLeft(0); setRight(TURN_PWM);
  } else if (IRL == HIGH && IRR == LOW) {
    setLeft(TURN_PWM); setRight(0);
  } else {
    stopMotors();
  }
}

/*
  No historical conversion/scale was preserved. This implementation maps
  each raw RGB channel into a proportion of a total of 10. The Pi uses the
  exact documented rule: r>=4 || r>=2*g || r>=2*b. The latter is also true
  for 0:0:0; this is a documented property of the original expression.
*/
void readColorScores(uint8_t &r, uint8_t &g, uint8_t &b) {
  uint16_t rawR = 0, rawG = 0, rawB = 0, rawClear = 0;
  tcs.getRawData(&rawR, &rawG, &rawB, &rawClear);
  const uint32_t sum = (uint32_t)rawR + rawG + rawB;
  if (sum == 0) { r = 0; g = 0; b = 0; return; }
  r = (uint8_t)((uint32_t)rawR * 10UL / sum);
  g = (uint8_t)((uint32_t)rawG * 10UL / sum);
  b = (uint8_t)((uint32_t)rawB * 10UL / sum);
}

// A complete one-character LF-terminated reply only. Other data => STOP.
// Purging stale bytes prior to each request makes old replies less likely,
// but 0/1 legacy packets have no sequence numbers: cannot guarantee matching.
void flushOldReplies() {
  while (Serial.available() > 0) (void)Serial.read();
}

bool readMotionPermission(bool &allowMotion) {
  char data[4] = {0, 0, 0, 0};
  uint8_t used = 0;
  const unsigned long started = millis();
  while (millis() - started < RESPONSE_TIMEOUT_MS) {
    if (Serial.available() <= 0) continue;
    const char ch = (char)Serial.read();
    if (ch == '\r') continue;
    if (ch == '\n') {
      if (used != 1 || (data[0] != '0' && data[0] != '1')) return false;
      allowMotion = (data[0] == '1');
      return true;
    }
    if (used >= sizeof(data)) return false;
    data[used++] = ch;
  }
  return false;
}

void setup() {
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(IRL_PIN, INPUT);
  pinMode(IRR_PIN, INPUT);
  pinMode(LmotorCW, OUTPUT); pinMode(LmotorCCW, OUTPUT);
  pinMode(RmotorCW, OUTPUT); pinMode(RmotorCCW, OUTPUT);
  stopMotors();
  Serial.begin(SERIAL_BAUD);
  if (!tcs.begin()) {
    while (true) { stopMotors(); delay(250); }
  }
}

void loop() {
  uint8_t r, g, b;
  readColorScores(r, g, b);
  // INPUT_PULLUP -> LOW on press, transmit semantic value 1
  const uint8_t button = digitalRead(BUTTON_PIN) == LOW ? 1 : 0;

  flushOldReplies();
  Serial.print(r); Serial.print(':');
  Serial.print(g); Serial.print(':');
  Serial.print(b); Serial.print(':');
  Serial.println(button);

  bool allowMotion = false;
  if (readMotionPermission(allowMotion) && allowMotion) followLine();
  else stopMotors(); // timeout, corrupted message, Pi stop result
  delay(IDLE_DELAY_MS);
}
