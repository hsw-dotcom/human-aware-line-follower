#define LmotorCW 5
#define LmotorCCW 6

#define RmotorCW 9
#define RmotorCCW 10

#define IRL 7
#define IRR 8
#define BUTTON_PIN 3 // 3핀 푸시 버튼

#include <Wire.h>
#include "Adafruit_TCS34725.h"

int speed = 255;
bool buttonPressed = false; // 푸시 버튼 상태를 저장하는 변수
unsigned long lastColorCheckTime = 0; // 마지막으로 색상 확인한 시간
unsigned long buttonPressTime = 0; // 버튼을 누른 시간을 저장하는 변수

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
  delay(100);

  if (!TCS.begin()) {
    Serial.println("No TCS34725 found ... check your connections");
    while (1);
  }
  else {
    Serial.println("Found sensor");
  }
}

void loop() {
  // 버튼을 누르기 전까지는 로봇이 정지된 상태
  if (!buttonPressed) {
    analogWrite(LmotorCW, 0);
    analogWrite(LmotorCCW, 0);
    analogWrite(RmotorCW, 0);
    analogWrite(RmotorCCW, 0);
  }

  // 버튼을 누르면 움직이도록 설정
  if (digitalRead(BUTTON_PIN) == LOW) {
    buttonPressed = true;
    buttonPressTime = millis();
    while (millis() - buttonPressTime < 500) {
      analogWrite(LmotorCW, 0);
      analogWrite(LmotorCCW, speed);
      analogWrite(RmotorCW, speed);
      analogWrite(RmotorCCW, 0);
    }
  }

  if (buttonPressed) {
    if (Serial.available() > 0) {
      int receivedNumber = Serial.parseInt();
      Serial.print("Received number: ");
      Serial.println(receivedNumber);
      // 일정한 간격(1초)으로만 색상을 확인하도록 수정
      unsigned long currentTime = millis();
      if (currentTime - lastColorCheckTime >= 1000) {
        lastColorCheckTime = currentTime;

        uint16_t clear, red, green, blue;
        TCS.getRawData(&red, &green, &blue, &clear);

        int r = map(red, 0, 21504, 0, 1025);
        int g = map(green, 0, 21504, 0, 1025);
        int b = map(blue, 0, 21504, 0, 1025);

        Serial.print("   R: ");
        Serial.print(r);
        Serial.print("   G: ");
        Serial.print(g);
        Serial.print("   B: ");
        Serial.println(b);

        // 색상 조건, 사람 조건을 만족하면 로봇을 멈춤
        if (r >= 5 || receivedNumber >= 1) {
          analogWrite(LmotorCW, 0);
          analogWrite(LmotorCCW, 0);
          analogWrite(RmotorCW, 0);
          analogWrite(RmotorCCW, 0);
        } else {
          // 색상 조건을 만족하지 않으면 로봇을 움직임
          if (digitalRead(IRL) == HIGH && digitalRead(IRR) == HIGH) {
            analogWrite(LmotorCW, 0);
            analogWrite(LmotorCCW, speed);
            analogWrite(RmotorCW, speed);
            analogWrite(RmotorCCW, 0);
          } else if (digitalRead(IRL) == LOW && digitalRead(IRR) == HIGH) {
            analogWrite(LmotorCW, 0);
            analogWrite(LmotorCCW, speed);
            analogWrite(RmotorCW, 0);
            analogWrite(RmotorCCW, speed);
          } else if (digitalRead(IRL) == HIGH && digitalRead(IRR) == LOW) {
            analogWrite(LmotorCW, speed);
            analogWrite(LmotorCCW, 0);
            analogWrite(RmotorCW, speed);
            analogWrite(RmotorCCW, 0);
          } else if (digitalRead(IRL) == LOW && digitalRead(IRR) == LOW) {
            analogWrite(LmotorCW, 0);
            analogWrite(LmotorCCW, 0);
            analogWrite(RmotorCW, 0);
            analogWrite(RmotorCCW, 0);
          }
        }
      }
    }
  }
}
