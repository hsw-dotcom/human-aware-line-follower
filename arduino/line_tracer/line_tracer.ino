/*
 * 사람 인식 기반 라인트레이서 — 2026년 역할 분담 교정 복원본.
 * 2023년 실제 최종 .ino 원문은 아직 확보하지 못했습니다.
 *
 * 확인된 역할:
 *   Raspberry Pi: 사람 검출 → 존재 여부를 0/1로 변환해 송신
 *   Arduino: TCS34725 정지구간 감지 + Pi의 사람 존재 신호로 정지 판단
 *            IR 라인 추종, 버튼 재출발
 *
 * 현재 복원에서 선택한 신호 극성(최종 과거 원문 미확인):
 *   1 = 사람 인식, 0 = 사람 없음
 * 실제 Arduino 개발 스케치에는 'receivedNumber != 0이면 정지'가 존재함.
 *
 * 모터 핀·IR 핀·버튼 핀·9600bps·255는 사용자 제공 스케치를 따름.
 * 아래 색상 역치(r >= 5)는 사용자 제공 01 시험 스케치에서 선택.
 * 2026-10-31 사용자 확인: 사람 인식은 0.3초 주기로 갱신하고,
 * 색상 정지구간은 라벨/테이프 재질의 색에 따라 기준을 조정했으며,
 * 정지 후 버튼 전까지 정지 유지, 재출발 직후 두 정지 조건 모두 무시.
 * 최종 채택된 RGB 환산식·정지구간 역치·재출발 무시 시간은 미확인.
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

const int driveSpeed = 255;
const int STOP_ZONE_RED_MIN = 5;         // 라벨·테이프 색에 맞춰 조정했던 시험값; 최종값 미확인
const unsigned long IGNORE_MS = 2000;    // 1~3초 실험 중 대표값; 최종값 아님

Adafruit_TCS34725 TCS =
    Adafruit_TCS34725(TCS34725_INTEGRATIONTIME_50MS, TCS34725_GAIN_4X);

bool personDetected = false;            // Pi에서 수신한 마지막 0/1
bool stoppedForLoading = false;
bool buttonWasDown = false;
bool ignoringStopConditions = false;  // 버튼 후 사람·색상 두 정지 조건 모두 무시
unsigned long restartTime = 0;

void stopMotor() {
  analogWrite(LmotorCW, 0);
  analogWrite(LmotorCCW, 0);
  analogWrite(RmotorCW, 0);
  analogWrite(RmotorCCW, 0);
}

void forward() {
  analogWrite(LmotorCW, 0);
  analogWrite(LmotorCCW, driveSpeed);
  analogWrite(RmotorCW, driveSpeed);
  analogWrite(RmotorCCW, 0);
}

void left() {
  analogWrite(LmotorCW, driveSpeed);
  analogWrite(LmotorCCW, 0);
  analogWrite(RmotorCW, driveSpeed);
  analogWrite(RmotorCCW, 0);
}

void right() {
  analogWrite(LmotorCW, 0);
  analogWrite(LmotorCCW, driveSpeed);
  analogWrite(RmotorCW, 0);
  analogWrite(RmotorCCW, driveSpeed);
}

void lineTrace() {
  int l = digitalRead(IRL);
  int r = digitalRead(IRR);
  if (l == HIGH && r == HIGH) forward();
  else if (l == LOW && r == HIGH) left();
  else if (l == HIGH && r == LOW) right();
  else stopMotor();
}

void updatePersonSignal() {
  // ASCII 0/1만 제어 신호로 처리, 줄바꿈은 무시.
  // 2023년 최종 송신 종료문자는 미확인.
  while (Serial.available() > 0) {
    int c = Serial.read();
    if (c == '1') personDetected = true;
    else if (c == '0') personDetected = false;
  }
}

bool isStopZone() {
  // RGB 읽기/환산은 사용자 제공 초기 TCS34725 스케치를 참고.
  uint16_t red, green, blue, clear;
  TCS.getRawData(&red, &green, &blue, &clear);
  int r = map(red, 0, 21504, 0, 1025);
  // 당시 정지구간의 최종 판정식은 확인되지 않았습니다.
  return r >= STOP_ZONE_RED_MIN;
}

void setup() {
  pinMode(LmotorCW, OUTPUT);
  pinMode(LmotorCCW, OUTPUT);
  pinMode(RmotorCW, OUTPUT);
  pinMode(RmotorCCW, OUTPUT);
  pinMode(IRL, INPUT);
  pinMode(IRR, INPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  Serial.begin(9600);
  stopMotor();

  if (!TCS.begin()) {
    // 개발 스케치의 센서 초기화 실패 시 중단 방식을 따름.
    while (true) stopMotor();
  }
}

void loop() {
  updatePersonSignal();

  bool buttonDown = (digitalRead(BUTTON_PIN) == LOW);
  if (buttonDown && !buttonWasDown) {
    stoppedForLoading = false;
    ignoringStopConditions = true;
    restartTime = millis();
  }
  buttonWasDown = buttonDown;

  if (ignoringStopConditions && millis() - restartTime >= IGNORE_MS) {
    ignoringStopConditions = false;
  }

  // 버튼 재출발 직후에는 '사람 있음' 신호와 정지구간 색상을 모두
  // 정지 판단에 사용하지 않음. IR 라인 추종만 계속함.
  // Pi의 촬영 자체를 중단한다는 뜻은 아님(그런 연동 기록은 없음).
  if (ignoringStopConditions) {
    lineTrace();
    return;
  }

  // 정지구간은 Arduino가 직접 읽으며, Pi가 보낸 0/1 존재 신호와 AND 판정.
  bool stopZone = isStopZone();
  if (stopZone && personDetected) {
    stoppedForLoading = true;
  }

  // 한 번 멈춘 후에는 버튼을 누르기 전까지 정지 상태 유지.
  if (stoppedForLoading) stopMotor();
  else lineTrace();
}
