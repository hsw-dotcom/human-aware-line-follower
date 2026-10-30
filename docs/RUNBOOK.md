# 실행, 테스트, 원본 연동 절차

## 1. PC에서 먼저 검증

```bash
python3 -m unittest discover -s tests -v
python3 simulation/demo.py
```

하드웨어 없이 Python 상태변화만 확인합니다. Python 3.10 이상 권장(타입 힌트).

## 2. Arduino 준비

- Arduino IDE + 해당 보드 코어, `Adafruit TCS34725` 라이브러리 설치.
- `arduino/line_tracer/line_tracer.ino`를 열어 IRL/IRR(현재 **가정**: 2/4), 좌우 모터 방향 및 PWM을 확인.
- 버튼 INPUT_PULLUP과 핀 3의 접지 눌림 상태 확인.
- 색상 센서의 RGB 값·조도에 따라 실제 기록식이 발화되는지 먼저 관찰.
- 시리얼은 업무 메시지 전용이므로 `Serial.println("debug")` 금지.

## 3. Raspberry Pi 준비

- Raspberry Pi OS + 카메라 연결; Picamera2, OpenCV, PySerial 설치. OS 패키지와 Python 가상환경 혼용 시 라이브러리 경로를 확인.
- `cp raspberry_pi/config.example.ini raspberry_pi/config.ini`.
- `config.ini`에서 포트(`/dev/ttyACM0` 예제), 처리 주기, 이미지 저장 디렉터리, 재출발 무시 시간(1~3초), 해상도 설정.
- 예제 기본 사람 검출은 OpenCV HOG. 당시에 사용한 `count_objects` 모델을 보유했다면 `count_objects.py`를 해당 모델 인터페이스에 맞게 교체.

```bash
cd raspberry_pi
python3 -m line_tracer.main --config config.ini
```

## 4. 안전 점검

1. **바퀴를 바닥에서 띄운 채** 테스트한다.
2. Pi 분리, 잘못된 직렬 응답, 카메라 에러 → 정지를 확인한다.
3. HIGH/HIGH→직진, LOW/HIGH→좌, HIGH/LOW→우, LOW/LOW→정지 여부 확인.
4. RGB값을 여러 바닥색에서 기록하여 `r>=4 or r>=2*g or r>=2*b`의 트리거 범위를 관찰.
5. Pi 영상 저장(`runtime/before.jpg`) 및 검출 성능 측정.
6. 인식 구간에 진입하면 이전 결과와 관계없이 정지(0), 버튼은 재출발(1), 이후 1~3초 무시 여부를 확인.
7. 저속·통제된 장소에서 전원 단절, 잘못된 배선 등 별도 시험.

## 5. 여전히 불확실한 사항

- Arduino IDE 실제 컴파일, 물리 배선, TCS34725 정규화와 해당 바닥색의 수치
- Pi 카메라 모델/픽셀 형식, 지연·실제 프레임 속도
- 사람 인식 3~5m 재현성, 원본 객체 탐지 모델
- 역사적 원본과 동일한 타이밍/오작동 여부
