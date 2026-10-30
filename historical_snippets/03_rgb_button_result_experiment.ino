#include <Wire.h>
#include "Adafruit_TCS34725.h"

#define LmotorCW 5
#define LmotorCCW 6
#define RmotorCW 9
#define RmotorCCW 10
#define IRL 7
#define IRR 8
#define BUTTON_PIN 3 // 버튼 핀

int speed = 255;
int result = 0; // 초기값 0으로 설정

Adafruit_TCS34725 TCS = Adafruit_TCS34725(TCS34725_INTEGRATIONTIME_50MS, TCS34725_GAIN_4X);

void setup() {
  pinMode(LmotorCW, OUTPUT);
  pinMode(LmotorCCW, OUTPUT);
  pinMode(RmotorCW, OUTPUT);
  pinMode(RmotorCCW, OUTPUT);
  pinMode(IRL, INPUT);
  pinMode(IRR, INPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP); // 풀업 저항을 이용하여 버튼 핀 입력 설정

  Serial.begin(9600);

  if (!TCS.begin()) {
    Serial.println("No TCS34725 found ... check your connections");
    while (1);
  } else {
    Serial.println("Found sensor");
  }
}

void loop() {
  int red, green, blue;

  // 색상값 읽기
  uint16_t clear;
  getRGBValues(red, green, blue);

  // 버튼 상태 읽기
  int button = digitalRead(BUTTON_PIN);

  // 시리얼로 색상값 및 버튼 상태 출력 및 라즈베리 파이로 전송
  Serial.print("ColorValues:");
  Serial.print(red);
  Serial.print(",");
  Serial.print(green);
  Serial.print(",");
  Serial.println(blue);

  Serial.print("ButtonState:");
  Serial.println(button);

  // 라즈베리 파이로부터의 값을 읽기
  if (Serial.available() > 0) {
    result = Serial.read();
    Serial.print("Received result from Raspberry Pi: ");
    Serial.println(result);
  }

  // result 값에 따른 동작
  if (result == 0) {
    // 정지
    analogWrite(LmotorCW, 0);
    analogWrite(LmotorCCW, 0);
    analogWrite(RmotorCW, 0);
    analogWrite(RmotorCCW, 0);
  } else if (result == 1) {
    // 센서에 따라 동작
    if (digitalRead(IRL) == HIGH && digitalRead(IRR) == HIGH) {
      // 양쪽 센서 모두 감지되면 전진
      analogWrite(LmotorCW, 0);
      analogWrite(LmotorCCW, speed);
      analogWrite(RmotorCW, speed);
      analogWrite(RmotorCCW, 0);
    } else if (digitalRead(IRL) == LOW && digitalRead(IRR) == HIGH) {
      // 왼쪽 센서만 감지되면 왼쪽으로 회전
      analogWrite(LmotorCW, 0);
      analogWrite(LmotorCCW, speed);
      analogWrite(RmotorCW, 0);
      analogWrite(RmotorCCW, speed);
    } else if (digitalRead(IRL) == HIGH && digitalRead(IRR) == LOW) {
      // 오른쪽 센서만 감지되면 오른쪽으로 회전
      analogWrite(LmotorCW, speed);
      analogWrite(LmotorCCW, 0);
      analogWrite(RmotorCW, speed);
      analogWrite(RmotorCCW, 0);
    } else if (digitalRead(IRL) == LOW && digitalRead(IRR) == LOW) {
      // 양쪽 센서 모두 감지되지 않으면 정지
      analogWrite(LmotorCW, 0);
      analogWrite(LmotorCCW, 0);
      analogWrite(RmotorCW, 0);
      analogWrite(RmotorCCW, 0);
    }
  }
}

void getRGBValues(int &red, int &green, int &blue) {
  // 실제 센서값을 읽어와 RGB 값으로 변환
  uint16_t clear;
  TCS.getRawData(&red, &green, &blue, &clear);

  // 여기에 필요한 범위 조정 및 스케일링 로직 추가 가능
  red = map(red, 0, 21504, 0, 1025);
  green = map(green, 0, 21504, 0, 1025);
  blue = map(blue, 0, 21504, 0, 1025);
}
