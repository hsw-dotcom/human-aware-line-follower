# Raspberry Pi 코드 정리 — 2023년 대화 기록과 현행 복원본

> 목적: **Pi에 실제로 입력했던 코드의 근거**와, 당시 ChatGPT가 제안한 수정·현재 복원 코드를 구분합니다.
> 실제 2023년 라인트레이서용 `main.py` 전체 파일과 추출된 `count_objects.py` 전체 원문은 아직 확보되지 않았습니다.
> '실제 코드'로 공개 가능한 텍스트는 사용자 제공 시리얼 테스트 코드와 Safe Watch의 원본 소스이며, 나머지는 확인된 부분만 기록합니다.

## 1. 개발 단계별 근거

| 구분 | 시점·근거 | 확인 가능한 내용 | 분류 |
|---|---|---|---|
| 카메라·검출 함수 재사용 | 2023-11-23 사용자 대화 | `get_frame(ip)`, `count_objects.detect()`, `before.jpg` 저장, 카메라 스트림에서 프레임 가져오기 | 당시 사용자 코드의 부분 기록 |
| 시리얼 연결 시작 | 2023-11-23 사용자 대화 | `send_data_to_arduino(ser, data)` 사용; 수신·송신 경로 시험 | 당시 사용자 코드의 부분 기록 |
| 시리얼 송수신 독립 시험 | 사용자 제공 `02_serial_echo_test.py` 원문 | `serial.Serial('/dev/ttyACM0', 9600, timeout=1)`, `readline().decode('utf-8').strip()`, `ser.write(...encode())` | 실제 제공된 전체 코드 |
| Pi 메인 루프 | 2023-11-24 사용자 대화 | `/home/pi/project/main.py`, `get_ip()`, `get_frame(ip)`, `count_object()`, `send_data_to_arduino(ser, data)` 등 | 당시 사용자 코드의 함수·설정 기록, 전체 미확보 |
| Arduino 패킷 파싱 | 2023-11-24 문답 | Arduino의 `r:g:b:button`을 수신해 `map(int, serial_data.split(':'))`로 해석하도록 제안 | 대화의 수정 제안 및 사용자 요구 |
| 결과값 회신 | 2023-11-24 문답 | `send_data_to_arduino(ser, result)`, `ser.write(f"{result}".encode())` 제안 | ChatGPT 제안; 실제 최종 실행 여부 미확인 |
| 최종 판단 규칙 | 당시 후속 문답 | 버튼 1→결과 1, 색상 조건 또는 사람 수 비0→결과 0, 그 외 이전 값 유지 | 대화의 최종 조건식 기록 |
| 감지 지연·재출발 | 사용자 회고 | 사람 감지로 실제 정지 성공, 검출 연산 간소화, 감지 시점 선행, 적재 후 버튼으로 색상 정지 구간 일시 무시 | 실장 경험 확인; 대응하는 전체 소스 미확보 |

**주의:** 표의 날짜는 해당 대화가 확인된 시점이지 모든 파일의 생성일이나 실제 Arduino–Pi 통합 버전의 최종 시험일이 아닙니다. 특히 날짜가 다른 코드 조각을 임의로 하나의 '실제 원본'으로 합치지 않습니다.

## 2. 현재 저장소의 Pi 관련 코드 위치

| 파일 | 용도 | 원본 여부 |
|---|---|---|
| [`historical_snippets/02_serial_echo_test.py`](../historical_snippets/02_serial_echo_test.py) | 독립 시리얼 송수신 테스트; 원문 그대로 보존 | **사용자 제공 원문** |
| [`raspberry_pi/main.py`](../raspberry_pi/main.py) | 카메라 촬영·패킷 수신·판단·응답을 하나의 루프로 엮은 코드 | **2026년 복원본** |
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

## 4. 원본 경로와 데이터 형식의 충돌

- **프레임 경로**: 2023-11-23 라인트레이서 개발 대화에서 `/home/pi/project/before.jpg`가 사용된 흔적이 있습니다. 별도로 확인된 Safe Watch 원본은 `/home/pi/project/image/before.jpg`입니다. 현재 Pi 복원본은 후자의 경로로 통일했으나 **역사적 최종 경로와 동일하다는 증거는 없습니다**.
- **시리얼 장치명**: 2023년 초기 예시는 `/dev/ttyUSB0`도 등장했지만, 사용자 제공 코드는 `/dev/ttyACM0` 및 `9600`을 포함합니다. 실제 시스템에서 사용한 포트를 코드마다 구분해야 합니다.
- **입력 형식**: 한 Arduino 시험 스케치는 `ColorValues:r,g,b`와 `ButtonState:`를 따로 전송합니다. 다른 대화에서는 `r:g:b:button`을 한 줄로 전송하도록 결정합니다. 둘을 같은 시리얼 프로토콜이라고 취급하면 안 됩니다.
- **반환값 의미**: 일부 Arduino 스케치는 `receivedNumber != 0`일 때 정지합니다. 대화 기반 Pi 최종 판단식은 반대로 `result=0`을 정지로 정의합니다. **마지막으로 함께 실행된 Arduino·Pi 코드 쌍이 미확인**이므로 일방적으로 통일하지 않았습니다.
- **검출 반환형**: 원본 Safe Watch `count_objects.detect()`는 `(people_num, obstacle_classes)`를 반환합니다. 현재 Pi 추출 복원본은 사람 수 정수만 반환하지만, 2023년 라인트레이서에 적용한 실제 추출본의 반환형은 모릅니다.

## 5. 복원본의 확인된 제어상 한계

현행 `raspberry_pi/main.py`는 **색 조건이 참일 때만** `detect_people()`를 호출합니다. 동시에 색 조건이 참이면 사람 수와 관계없이 결과가 `0`입니다. 따라서 **현재 복원 코드에서는 사람 인식 결과가 주행·정지를 바꾸지 못합니다**. 이는 당시 실제 장치에서 사람 감지 정지 시험에 성공했다는 사용자 경험과 구분해야 할 **복원상의 공백**입니다.

역사적 소스가 없는 상태에서 조건을 새로 바꾸어 '2023년 최종 코드'라고 표시하지 않습니다. 관련 검토: [제어 로직 감사](CONTROL_LOGIC_AUDIT.md).

## 6. 하드웨어 없이 확인할 수 있는 범위

```bash
python3 -m unittest discover -s tests -v
python3 simulation/trace.py
python3 -m py_compile raspberry_pi/main.py raspberry_pi/count_objects.py historical_snippets/02_serial_echo_test.py
```

이 명령은 Python 문법·제어 조건 일부만 확인합니다. 실제 카메라, Arduino 연결, 원본 TFLite 모델 추론이나 물리 정지를 확인하는 것은 아닙니다.
