#define LmotorCW     5
#define LmotorCCW    6
#define RmotorCW     9
#define RmotorCCW    10
#define IRL          7
#define IRR          8
#define BUTTON_PIN   3 // 3핀 푸시 버튼

#include <Wire.h>

int speed = 255;
unsigned long lastCommunicationTime = 0;
int receivedNumber = 0;
int moving = 0;

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

  // 0.3초 주기로 통신
  if (currentTime - lastCommunicationTime >= 300) {
    lastCommunicationTime = currentTime;

    if (Serial.available() > 0) {
      receivedNumber = Serial.parseInt();
      Serial.print("Received number: ");
      Serial.println(receivedNumber);
    }
  }

  // 버튼 상태 읽기
  int buttonState = digitalRead(BUTTON_PIN);

  // 버튼이 눌리면 로봇 상태 전환
  if (buttonState == LOW) {
    moving = 1;

    // 버튼이 눌린 상태에서 최대 0.3초 동안 move 함수 호출
    unsigned long buttonPressTime = millis();
    while (millis() - buttonPressTime < 300) {
      move();
    }
  }

  // receivedNumber가 0이 아닌 경우, 로봇 정지
  if (receivedNumber != 0) {
    moving = 0;
  }

  // 로봇이 움직이는 동안 move 함수 호출
  if (moving) {
    move();
  }
}

void stop() {
  analogWrite(LmotorCW, 0);
  analogWrite(LmotorCCW, 0);
  analogWrite(RmotorCW, 0);
  analogWrite(RmotorCCW, 0);
}

void move() {
  if (digitalRead(IRL) == HIGH && digitalRead(IRR) == HIGH) {
    forward();
  } else if (digitalRead(IRL) == LOW && digitalRead(IRR) == HIGH) {
    left();
  } else if (digitalRead(IRL) == HIGH && digitalRead(IRR) == LOW) {
    right();
  } else if (digitalRead(IRL) == LOW && digitalRead(IRR) == LOW) {
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
  analogWrite(LmotorCW, 0);
  analogWrite(LmotorCCW, speed);
  analogWrite(RmotorCW, 0);
  analogWrite(RmotorCCW, speed);
}

void right() {
  analogWrite(LmotorCW, speed);
  analogWrite(LmotorCCW, 0);
  analogWrite(RmotorCW, speed);
  analogWrite(RmotorCCW, 0);
}
