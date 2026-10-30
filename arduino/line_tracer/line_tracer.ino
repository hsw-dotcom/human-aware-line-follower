/*
 * Arduino 정지구간·모터 제어 복원 예시 (2023년 최종 원본 아님).
 * Pi: 0=사람 없음, 1=사람 있음 / Arduino: 정지구간 판별
 * 색상 임계값과 재출발 무시 시간은 개발 실험에 근거한 예시값.
 */
#include <Wire.h>
#include <Adafruit_TCS34725.h>

#define LmotorCW 5
#define LmotorCCW 6
#define RmotorCW 9
#define RmotorCCW 10
#define IRL 7
#define IRR 8
#define BUTTON_PIN 3

const int SPEED = 255;
const int RED_THRESHOLD = 5;      // 라벨·테이프 색상에 맞춰 조정
const unsigned long IGNORE_MS = 2000;  // 시험 예시값, 최종값 미확인

Adafruit_TCS34725 sensor(
    TCS34725_INTEGRATIONTIME_50MS, TCS34725_GAIN_4X);

bool personPresent = false;
bool stopped = false;
bool wasButtonDown = false;
bool ignoringConditions = false;
unsigned long restartedAt = 0;

void motors(int lCW, int lCCW, int rCW, int rCCW) {
  analogWrite(LmotorCW, lCW);
  analogWrite(LmotorCCW, lCCW);
  analogWrite(RmotorCW, rCW);
  analogWrite(RmotorCCW, rCCW);
}

void stopMotor() { motors(0, 0, 0, 0); }

void lineTrace() {
  int l = digitalRead(IRL), r = digitalRead(IRR);
  if (l == HIGH && r == HIGH) motors(0, SPEED, SPEED, 0);
  else if (l == LOW && r == HIGH) motors(SPEED, 0, SPEED, 0);
  else if (l == HIGH && r == LOW) motors(0, SPEED, 0, SPEED);
  else stopMotor();
}

void receivePersonFlag() {
  while (Serial.available()) {
    int incoming = Serial.read();
    if (incoming == '0') personPresent = false;
    else if (incoming == '1') personPresent = true;
  }
}

bool atStopZone() {
  uint16_t r, g, b, clear;
  sensor.getRawData(&r, &g, &b, &clear);
  int red = map(r, 0, 21504, 0, 1025);
  return red >= RED_THRESHOLD;
}

void setup() {
  pinMode(LmotorCW, OUTPUT); pinMode(LmotorCCW, OUTPUT);
  pinMode(RmotorCW, OUTPUT); pinMode(RmotorCCW, OUTPUT);
  pinMode(IRL, INPUT); pinMode(IRR, INPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  Serial.begin(9600);
  stopMotor();
  if (!sensor.begin()) while (true) stopMotor();
}

void loop() {
  receivePersonFlag();

  bool buttonDown = digitalRead(BUTTON_PIN) == LOW;
  if (buttonDown && !wasButtonDown) {
    stopped = false;
    ignoringConditions = true;
    restartedAt = millis();
  }
  wasButtonDown = buttonDown;

  if (ignoringConditions && millis() - restartedAt >= IGNORE_MS)
    ignoringConditions = false;

  // 재출발 직후에는 색상과 사람 신호 모두 정지 판단에서 제외.
  if (!ignoringConditions && !stopped && personPresent && atStopZone())
    stopped = true;

  if (stopped) stopMotor();
  else lineTrace();
}
