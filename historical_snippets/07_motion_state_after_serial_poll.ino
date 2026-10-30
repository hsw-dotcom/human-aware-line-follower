#define LmotorCW 5
#define LmotorCCW 6
#define RmotorCW 9
#define RmotorCCW 10
#define IRL 7
#define IRR 8
#define BUTTON_PIN 3

#include <Wire.h>

int speed = 255;
unsigned long lastCommunicationTime = 0;
int receivedNumber = 0;
bool moving = false;

void setup() {
  pinMode(LmotorCW, OUTPUT);
  pinMode(LmotorCCW, OUTPUT);
  pinMode(RmotorCW, OUTPUT);
  pinMode(RmotorCCW, OUTPUT);

  pinMode(IRL, INPUT);
  pinMode(IRR, INPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  Serial.begin(9600);
}

void loop() {
  unsigned long currentTime = millis();

  // 0.3초 주기로 시리얼 통신 확인
  if (currentTime - lastCommunicationTime >= 300) {
    lastCommunicationTime = currentTime;

    if (Serial.available() > 0) {
      receivedNumber = Serial.parseInt();
    }

    // 통신 처리 후 주행 상태 확인
    if (moving && receivedNumber == 0) {
      move();
    }
  }

  // 버튼 상태 읽기
  int buttonState = digitalRead(BUTTON_PIN);

  // 버튼이 눌리면 주행 시작
  if (buttonState == LOW) {
    if (!moving) {
      moving = true;

      unsigned long buttonPressTime = millis();

      // 0.3초 동안 주행
      while (millis() - buttonPressTime < 300) {
        move();
      }
    }
  } else {
    // 버튼을 놓아도 주행 유지
    if (moving) {
      move();
    }
  }

  // 수신값이 0이 아니면 정지
  if (receivedNumber != 0) {
    stop();
    moving = false;
  }
}

void stop() {
  analogWrite(LmotorCW, 0);
  analogWrite(LmotorCCW, 0);
  analogWrite(RmotorCW, 0);
  analogWrite(RmotorCCW, 0);
}

void move() {
  if (digitalRead(IRL) == HIGH &&
      digitalRead(IRR) == HIGH) {
    forward();
  }
  else if (digitalRead(IRL) == LOW &&
           digitalRead(IRR) == HIGH) {
    left();
  }
  else if (digitalRead(IRL) == HIGH &&
           digitalRead(IRR) == LOW) {
    right();
  }
  else {
    stop();
  }
}

void forward() {
  analogWrite(LmotorCW, 0);
  analogWrite(LmotorCCW, speed);
  analogWrite(RmotorCW, speed);
  analogWrite(RmotorCCW, 0);
}

void left() {
  analogWrite(LmotorCW, speed);
  analogWrite(LmotorCCW, 0);
  analogWrite(RmotorCW, speed);
  analogWrite(RmotorCCW, 0);
}

void right() {
  analogWrite(LmotorCW, 0);
  analogWrite(LmotorCCW, speed);
  analogWrite(RmotorCW, 0);
  analogWrite(RmotorCCW, speed);
}