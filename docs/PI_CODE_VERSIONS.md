# Raspberry Pi 코드 정리 — 2023년 대화 기록과 현행 복원본

> 목적: **Pi에 실제로 입력했던 코드의 근거**와, 당시 ChatGPT가 제안한 수정·현재 복원 코드를 구분합니다.
> 실제 2023년 라인트레이서용 `main.py` 전체 파일과 추출된 `count_objects.py` 전체 원문은 아직 확보되지 않았습니다.
> **최종 역할 정정:** Pi는 사람 검출 후 0/1 존재 신호만 송신합니다. 정지구간 TCS34725와 버튼·모터는 Arduino가 처리합니다. 이 역할은 사용자 직접 확인입니다.
> '실제 코드'로 공개 가능한 텍스트는 사용자 제공 시리얼 테스트 코드와 Safe Watch의 원본 소스이며, 나머지는 확인된 부분만 기록합니다.

## 1. 개발 단계별 근거

| 구분 | 시점·근거 | 확인 가능한 내용 | 분류 |
|---|---|---|---|
| 카메라·검출 함수 재사용 | 2023-11-23 사용자 대화 | **`while True` 반복에서 `get_frame(ip)` → `count_object()`를 먼저 수행하고 이후 시리얼 송수신** | 당시 사용자 코드의 부분 기록 |
| 시리얼 연결 시작 | 2023-11-23 사용자 대화 | `send_data_to_arduino(ser, data)` 사용; 수신·송신 경로 시험 | 당시 사용자 코드의 부분 기록 |
| 시리얼 송수신 독립 시험 | 사용자 제공 `02_serial_echo_test.py` 원문 | `serial.Serial('/dev/ttyACM0', 9600, timeout=1)`, `readline().decode('utf-8').strip()`, `ser.write(...encode())` | 실제 제공된 전체 코드 |
| Pi 메인 루프 | 2023-11-24 사용자 대화 | `/home/pi/project/main.py`, `get_ip()`, `get_frame(ip)`, `count_object()`, `send_data_to_arduino(ser, data)` 등 | 당시 사용자 코드의 함수·설정 기록, 전체 미확보 |
| Arduino 패킷 파싱 | 2023-11-24 문답 | Arduino의 `r:g:b:button`을 수신해 `map(int, serial_data.split(':'))`로 해석하도록 제안 | 대화의 수정 제안 및 사용자 요구 |
| 결과값 회신(다른 설계) | 2023-11-24 문답 | `send_data_to_arduino(ser, result)`, `ser.write(f"{result}".encode())` 제안 | 당시 논의한 다른 설계, 최종 역할과 다름 |
| 최종 판단 규칙 | 당시 후속 문답 | 버튼 1→결과 1, 색상 조건 또는 사람 수 비0→결과 0, 그 외 이전 값 유지 | 대화의 최종 조건식 기록 |
| 감지 지연·재출발 | 사용자 회고 | 사람 감지로 실제 정지 성공, 검출 연산 간소화, 감지 시점 선행, 적재 후 버튼으로 색상 정지 구간 일시 무시 | 실장 경험 확인; 대응하는 전체 소스 미확보 |

**주의:** 표의 날짜는 해당 대화가 확인된 시점이지 모든 파일의 생성일이나 실제 Arduino–Pi 통합 버전의 최종 시험일이 아닙니다. 특히 날짜가 다른 코드 조각을 임의로 하나의 '실제 원본'으로 합치지 않습니다.

## 2. 현재 저장소의 Pi 관련 코드 위치

| 파일 | 용도 | 원본 여부 |
|---|---|---|
| [`historical_snippets/02_serial_echo_test.py`](../historical_snippets/02_serial_echo_test.py) | 독립 시리얼 송수신 테스트; 원문 그대로 보존 | **사용자 제공 원문** |
| [`raspberry_pi/main.py`](../raspberry_pi/main.py) | 카메라 촬영·사람 검출·인원 수를 존재 여부 0/1로 변환 후 송신만 수행 | **2026년 역할 교정 복원본** |
| [`raspberry_pi/count_objects.py`](../raspberry_pi/count_objects.py) | Safe Watch에서 사람 검출만 추출한 기능적 복원 | **2026년 추출 복원본**, 당시 추출 파일 원문 아님 |
| [`tests/`](../tests/) | 상태 및 사람 수 판정의 오프라인 테스트 | 새로 만든 검증 코드 |
| [`simulation/trace.py`](../simulation/trace.py) | 임의의 센서값을 넣어 제어 상태 모의 | 새로 만든 검증 코드 |
| [Safe Watch `src/python/count_objects.py`](https://github.com/hsw-dotcom/safe-watch-crowd-monitoring/blob/main/src/python/count_objects.py) | 실제 원본 사람 검출 기능의 출처 | **별도 프로젝트에서 확보된 원본** |

`historical_snippets/02_serial_echo_test.py`는 초보 단계의 시리얼 실험이며 2023년의 **최종 Pi 메인 프로그램**이 아닙니다.

## 3. 대화에서 확인된 Pi 로직 조각

다음 조각은 당시 대화에 나온 함수명, 통신 형식과 판단식을 정리한 것입니다. 하나의 2023년 파일에서 연속으로 복사한 원문이 아닙니다.

```python
# Arduino -> Pi: r:g:b:button
r, g, b, button = map(int, serial_data.split(':'))

# 사용자와 대화에서 확정한 판단 조건
color_condition = (r >= 4 or r >= 2*g or r >= 2*b)
if button == 1:
    result = 1
elif (color_condition == 1 or people_num != 0) and button == 0:
    result = 0
else:
    result = previous_result

# Pi -> Arduino: result
send_data_to_arduino(ser, result)
```

또 다른 2023-11-24 대화에서는 `get_serial_data(ser)`의 `ser.readline().decode().strip()`, `send_data_to_arduino(ser,result)`의 `ser.write(f"{result}".encode())`가 제안되었습니다. 이것이 물리 시험 당시 사용한 최종 전송 코드인지는 확인되지 않았습니다.

## 추가로 확인된 11월 24·28일 통신 실험

- **2023-11-24 사용자 요구:** Arduino로는 `current_result` 하나를 보내고 **이전 결과와 값이 다를 때만 전송**. 현재 실행용 복원본이 매 입력에 응답하도록 작성된 것은 별도의 통신 계약에 따른 선택입니다.
- **2023-11-28 사용자 제공 코드:** `people_num` 정수를 `ser.write(data.encode())`로 보내려다가 예외가 발생했고 `bytes([data])`로 수정해 시험했습니다. 이 raw byte 전송은 Arduino `Serial.parseInt()`와 호환되지 않아 정상 정지로 입증되지 않았습니다.
- **카메라 입력:** 사용자 `get_ip()`는 `wlan0`를 확인하고 `get_frame(ip)`는 `http://<ip>:8000/stream.mjpg`의 프레임을 OpenCV로 읽습니다. 현 복원에 이 경로를 반영했으나 모델/카메라 실기기 검증은 하지 않았습니다.

[통신·오류 기록](PI_SERIAL_AND_DEBUG_HISTORY.md) · [개발대화 재대조](CHAT_HISTORY_AUDIT.md).

## 4. 원본 경로와 데이터 형식의 충돌

- **프레임 경로**: 2023-11-23 라인트레이서 개발 대화에서 `/home/pi/project/before.jpg`가 사용된 흔적이 있습니다. 별도로 확인된 Safe Watch 원본은 `/home/pi/project/image/before.jpg`입니다. 현재 Pi 복원본은 후자의 경로로 통일했으나 **역사적 최종 경로와 동일하다는 증거는 없습니다**.
- **시리얼 장치명**: 2023년 초기 예시는 `/dev/ttyUSB0`도 등장했지만, 사용자 제공 코드는 `/dev/ttyACM0` 및 `9600`을 포함합니다. 실제 시스템에서 사용한 포트를 코드마다 구분해야 합니다.
- **입력 형식**: 한 Arduino 시험 스케치는 `ColorValues:r,g,b`와 `ButtonState:`를 따로 전송합니다. 다른 대화에서는 `r:g:b:button`을 한 줄로 전송하도록 결정합니다. 둘을 같은 시리얼 프로토콜이라고 취급하면 안 됩니다.
- **반환값 의미**: 과거 실험에는 `receivedNumber != 0` 정지 코드와 `result=0` 정지 코드가 모두 있습니다. **실제 최종 역할은 Pi=사람 존재 신호, Arduino=색상 및 정지 판단**으로 확인됐으며, 최종 신호의 정확한 극성은 아직 미확인입니다.
- **검출 반환형**: 원본 Safe Watch `count_objects.detect()`는 `(people_num, obstacle_classes)`를 반환합니다. 현재 Pi 추출 복원본은 사람 수 정수만 반환하지만, 2023년 라인트레이서에 적용한 실제 추출본의 반환형은 모릅니다.

## 5. 사용자 직접 확인한 최종 장치 역할과 현재 복원

**Pi는 사람 인식만 수행하고, 인원 수에 따른 사람 존재 여부 0/1로 계산해 Arduino에 송신합니다.** Arduino는 자체 TCS34725로 정지구간을 감지하고 Pi의 이진 값을 이용해 정지합니다. Pi는 RGB/버튼 패킷을 처리하거나 모터 정지 결과를 내리지 않습니다.

현재 Pi 복원 `main.py`는 사용자 코드에 근거한 `get_frame(ip)` 반복 추출·TFLite 사람 검출 후, `people_to_flag(people_num)`으로 0/1을 변환합니다. 2023-11-24 '값이 달라질 때만 전송' 요청에 따라 첫 송신과 변경 시에 ASCII 0/1을 보냅니다. **1=있음, 0=없음 극성과 최초 송신·개행은 원문 미확보 상태의 복원 선택입니다.**

위 3절에 있는 `색 OR 사람` 등은 **당시 개발 문답 기록**으로만 보존합니다. 2023년 원본 최종 파일과 이 복원본의 완전한 일치는 주장하지 않습니다. [최종 역할](FINAL_ROLE_DIVISION.md).

## 6. 하드웨어 없이 확인할 수 있는 범위

```bash
python3 -m unittest discover -s tests -v
python3 simulation/trace.py
python3 -m py_compile raspberry_pi/main.py raspberry_pi/count_objects.py historical_snippets/02_serial_echo_test.py
```

이 명령은 Python 문법·제어 조건 일부만 확인합니다. 실제 카메라, Arduino 연결, 원본 TFLite 모델 추론이나 물리 정지를 확인하는 것은 아닙니다.
