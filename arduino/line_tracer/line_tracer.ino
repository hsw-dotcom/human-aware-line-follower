/*
 * 2023.12 라인트레이서 — 대화 충실 복원 (실제 .ino 원문은 미확보)
 *
 * 확인된 숫자/규칙:
 *   LmotorCW=5, LmotorCCW=6, RmotorCW=9, RmotorCCW=10
 *   BUTTON_PIN=3, INPUT_PULLUP, 눌리면 button=1
 *   IRL/IRR: HH 전진, LH 좌회전, HL 우회전, LL 정지
 *   Arduino -> Pi: r:g:b:button / Pi -> Arduino: 0 또는 1
 * 미확인: IR 핀, 모터 속도, RGB의 축척, Serial 속도·종결자
 * 따라서 이런 값은 별도의 '가정'으로 표시하며 역사적 사실로 쓰지 않음.
 */
#include <Wire.h>
#include <Adafruit_TCS34725.h>

const int LmotorCW = 5;
const int LmotorCCW = 6;
const int RmotorCW = 9;
const int RmotorCCW = 10;
const int BUTTON_PIN = 3;

const int IRL_PIN = 2;         // 미확인, 동작을 설명하기 위한 임시 배선
const int IRR_PIN = 4;         // 미확인
const int DRIVE_SPEED = 150;  // 미확인
const long BAUD_RATE = 9600;  // 미확인

Adafruit_TCS34725 tcs = Adafruit_TCS34725();

void stopMotor() {
  analogWrite(LmotorCW, 0); analogWrite(LmotorCCW, 0);
  analogWrite(RmotorCW, 0); analogWrite(RmotorCCW, 0);
}

void lineTrace() {
  int IRL = digitalRead(IRL_PIN);
  int IRR = digitalRead(IRR_PIN);

  if (IRL == HIGH && IRR == HIGH) {        // 직진
    analogWrite(LmotorCW, DRIVE_SPEED); analogWrite(LmotorCCW, 0);
    analogWrite(RmotorCW, DRIVE_SPEED); analogWrite(RmotorCCW, 0);
  } else if (IRL == LOW && IRR == HIGH) {  // 좌회전
    analogWrite(LmotorCW, 0); analogWrite(LmotorCCW, 0);
    analogWrite(RmotorCW, DRIVE_SPEED); analogWrite(RmotorCCW, 0);
  } else if (IRL == HIGH && IRR == LOW) {  // 우회전
    analogWrite(LmotorCW, DRIVE_SPEED); analogWrite(LmotorCCW, 0);
    analogWrite(RmotorCW, 0); analogWrite(RmotorCCW, 0);
  } else {                                 // 정지
    stopMotor();
  }
}

void setup() {
  pinMode(IRL_PIN, INPUT); pinMode(IRR_PIN, INPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);
  pinMode(LmotorCW, OUTPUT); pinMode(LmotorCCW, OUTPUT);
  pinMode(RmotorCW, OUTPUT); pinMode(RmotorCCW, OUTPUT);
  Serial.begin(BAUD_RATE);
  tcs.begin();  // 실제 실패 처리 코드는 미확인
  stopMotor();
}

void loop() {
  float rf = 0, gf = 0, bf = 0;
  tcs.getRGB(&rf, &gf, &bf);  // TCS34725 입력 예시; 과거 구현의 축척은 미확인
  int r = (int)rf;
  int g = (int)gf;
  int b = (int)bf;
  int button = (digitalRead(BUTTON_PIN) == LOW) ? 1 : 0;

  Serial.print(r); Serial.print(':');
  Serial.print(g); Serial.print(':');
  Serial.print(b); Serial.print(':');
  Serial.println(button);

  // 값 0/1이 반환되면 모터 정지 또는 기존 IR 라인 추종 수행.
  // readStringUntil/줄바꿈 사용은 원본 미확인에 따른 최소한의 연결 방식.
  // 이전 스케치의 대기 방식은 미확인. 기본 readStringUntil 타임아웃에 의존.
  String response = Serial.readStringUntil('\n');
  response.trim();
  if (response == "0") stopMotor();
  else if (response == "1") lineTrace();
}
