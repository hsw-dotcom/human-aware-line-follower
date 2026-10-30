void setup() {
  Serial.begin(9600);
}

void loop() {
  if (Serial.available() > 0) {
    // Python으로부터 데이터 읽기
    String received_data = Serial.readStringUntil('\n');
    
    // 받은 데이터를 출력
    Serial.print("Arduino에서 받은 데이터: ");
    Serial.println(received_data);

    // 받은 데이터를 다시 Python으로 보내기
    Serial.print("Arduino에서 Python으로 데이터 전송: ");
    Serial.println(received_data);
  }
}
