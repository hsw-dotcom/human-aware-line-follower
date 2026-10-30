# 사람 인식 기반 라인트레이서 — 2023년 12월 대화 충실 복원본

> **2023년 당시 작성한 소스코드 원본 전문이 아닙니다.**
> 프로젝트 관련 과거 대화에서 확정된 코드·제어 규칙과 Safe Watch의 확인 가능한 사람 검출 소스를 근거로 복원한 최종 정리본입니다.
> 하드웨어가 없으므로 코드·논리·입출력 시뮬레이션만 검토합니다.


## Arduino 개발 스케치 7종 (사용자 제공 6종·후속 제안 1종)

실제로 제공된 Arduino 개발 코드 **6개**와 이번 대화의 **ChatGPT 후속 수정 제안 1개**를 구별해 보존했습니다. 제안 코드가 실제 Arduino에 업로드되었는지는 확인되지 않습니다. [스케치 보존 폴더](historical_snippets/)와 [버전별 검증 기록](docs/USER_SUPPLIED_ARDUINO_VERSIONS.md)에 **파일별로 원문 형태로 보관**했습니다.

- 제공된 스케치 여러 버전에서 **IR 센서 핀 7·8, PWM 5·6·9·10, 버튼 핀 3, 시리얼 9600bps**가 확인됩니다. 과거 코드 복원 시 임의로 가정했던 IR 핀 2·4보다 이 추가 증거를 우선합니다.
- RGB 원시값을 `map(raw, 0, 21504, 0, 1025)`로 변환하고, **300ms마다 통신을 검사하거나 1초마다 색상을 검사**하는 시험 버전이 있습니다. 이것을 최종 성능으로 단정하지는 않습니다.
- 시리얼 메시지 형식·`0/1`의 의미가 버전마다 달라 **기존 복원본의 `r:g:b:button` 계약이 유일한 최종 프로토콜이었다고 단정할 수 없습니다.**
- **6번 사용자 제공 스케치**에는 통신 시각 갱신 직후 100ms 경과 여부를 검사하는 **실행되지 않는 분기**가 있습니다. **7번 후속 제안 스케치**는 이 분기를 제거하고 `moving && receivedNumber == 0`일 때 `move()`하도록 바꿨습니다.
- 단, **7번도 버튼 입력 중 최대 약 300ms간 `move()`를 반복해 정지 처리가 지연될 수 있고**, `receivedNumber != 0`이 정지라는 점에서 기존 Python 재구성의 0/1 의미와 다릅니다. [버전별 검토](docs/USER_SUPPLIED_ARDUINO_VERSIONS.md)를 확인하세요.

**아래 통합 복원 코드(`arduino/line_tracer/line_tracer.ino`, `raspberry_pi/main.py`)는 원본 스케치와 별개입니다.** 어떤 스케치를 최종 실기기에 사용했는지는 아직 미확인입니다.

## Raspberry Pi Python 코드 정리

- [Pi 코드별 개발 흐름과 원본·수정 제안·복원본 구분](docs/PI_CODE_VERSIONS.md)
- [Pi 파일 안내](raspberry_pi/README.md)
- [실제 사용자 제공 시리얼 테스트 원문](historical_snippets/02_serial_echo_test.py)
- [Pi 역사적 코드 흔적의 범위](historical_snippets/PI_CODE_EVIDENCE.md)
- [**2023년 대화의 촬영 시점 근거**](docs/CAPTURE_TIMING_EVIDENCE.md)
- [**2023년 전체 개발대화 재대조 결과**](docs/CHAT_HISTORY_AUDIT.md)
- [**Pi–Arduino 시리얼 통신 실험과 오류 분석**](docs/PI_SERIAL_AND_DEBUG_HISTORY.md)
- [**최종 확인된 장치 역할 분담**](docs/FINAL_ROLE_DIVISION.md)

2023년 11월 23~28일 대화의 사용자 코드에서 **MJPEG 스트림 `get_frame()` → `count_objects.detect()` → Arduino 송수신**의 반복 순서를 확인했습니다. 정지구간 이후에야 촬영을 시작하는 분기는 없었습니다. 따라서 현재 Pi 복원은 **주행 중 반복 프레임 추출·검출을 먼저 수행하고, 이후 색상 센서의 정지구간 조건과 결합**합니다. 다른 기록에서 `send_data_to_arduino()`, `/dev/ttyACM0`, `9600bps` 등도 확인했습니다. **실제 최종 Pi `main.py` 전체 원문은 미확보**이며, 저장소의 `raspberry_pi/main.py`는 후대 복원본입니다.

## 프로젝트 개요

**최종 역할은 Pi=사람 인식 이진화, Arduino=정지구간 판정 및 모터 제어**입니다. 2026-10-31 사용자 직접 확인에 따라 이전의 'Pi가 RGB까지 받고 최종 정지를 판단'하던 복원 구조를 교정했습니다.

- **Raspberry Pi**: 주행 중 `wlan0` IP와 MJPEG `http://<ip>:8000/stream.mjpg`에서 반복 프레임 추출, Safe Watch 검출부로 인원수 계산, **사람 있음/없음만 0/1로 변환해 Arduino로 송신**. 인원 수 자체는 송신하지 않음
- **Arduino**: TCS34725로 **정지구간을 자체 감지**하고 Pi의 최신 0/1 사람 존재 신호와 결합해 정지 여부를 결정; IR 센서 라인 추종, 모터 제어와 적재 후 버튼 재출발도 수행
- **정지 시점**: 사람이 먼 거리에서 이미 인식돼도 계속 주행하며, **정지구간 센싱 AND 사람 인식 여부**가 모두 참일 때 정지
- **사람 인식값 갱신**: **0.3초 주기**(사용자 직접 확인). Pi가 검출값을 0/1로 변환하며, 현재 복원은 초기 1회 및 값 변경 시에만 전송
- **정지구간 표시**: 라벨·테이프로 바닥색을 다르게 구성하고, **재질의 색상에 따라 센서 판정 기준을 변경**
- **적재 후 재출발**: 버튼으로 정지 상태를 해제하고 **일정 시간 사람 신호와 정지구간 색상 조건 모두를 정지 판단에서 무시**. 1~3초 범위 시험, 최종 시간 미확인
- **모델 재사용**: Safe Watch TFLite의 사람 검출 부분만 추출해 사용했으며 새로운 AI 모델 학습을 담당했다는 의미가 아님

현재 복원에서 선택한 송신값은 `0=사람 없음`, `1=사람 있음`입니다. 이 극성은 Arduino 초기 제공 코드와 부합하지만 **2023년 최종 실행 파일의 극성까지 확인한 것은 아닙니다**. 2026년 복원본의 TCS34725 `r>=5` 역치와 `2000ms` 무시 시간 역시 시험 기록에 근거한 선택값일 뿐 확정된 최종값이 아닙니다. **고정된 하나의 색상이 아니라 현장에서 사용한 라벨·테이프 재질에 맞춰 기준을 조정한 것이 확정 사항**입니다.

[최종 역할 분담 상세](docs/FINAL_ROLE_DIVISION.md)

## 실제 시험 성공과 지연 문제 해결 (2023년 사용자 직접 확인)

**사람 인식 시 라인트레이서가 정지하는 실제 시험에 성공했습니다.** 다만 영상 인식 연산을 추가한 후 정지가 늦어져 **목표 적재 정지 구간을 지나치는 현상**이 발생했습니다. 이에 인식 연산을 간소화하고 **정지 구간보다 앞에서 감지하도록 조정**했습니다. 적재 후에는 **버튼을 다시 누르면 사람 존재 신호와 색상 정지구간 조건 모두를 일정 시간 무시하고 라인트레이싱을 재개**하도록 구성했습니다.

이 부분은 당시 실제 기기를 시험한 **사용자 직접 증언**에 기반합니다. 최적화 전후 지연시간, 인식 정확도, 반복 성공률 및 최종 실행 원문은 확보되지 않았습니다. [실제 시험·지연 개선 상세](docs/2023_FIELD_TEST_AND_LATENCY_IMPROVEMENT.md).

## 2023년 코드 재사용·통신 개발 화면

**Safe Watch의 객체 검출 코드를 추출해 라인트레이서에 사람 인식 기능을 적용하는 과정**의 화면들입니다. 당시 개발 흐름을 보여주는 자료이며, **이 사진만으로** 최종 라인트레이서의 자동 정지 성공률을 검증하는 것은 아닙니다. 실제 사람 인식 정지 성공은 별도 사용자 직접 확인에 근거합니다.

![기존 검출 코드 재사용 테스트 1 — 인물 영역 익명화](assets/2023_detector_reuse_test_redacted_1.jpg)

![기존 검출 코드 재사용 테스트 2 — 인물 영역 익명화](assets/2023_detector_reuse_test_redacted_2.jpg)

![Arduino–Raspberry Pi 시리얼 통신 시험 — 접속정보와 대화내용 가림](assets/2023_serial_test_redacted.jpg)

[화면별 근거와 해석 범위](docs/DETECTOR_REUSE_EVIDENCE.md)

## 역할 분담: 최종 목적과 이전 개발 실험의 차이

**최종 역할(사용자 직접 확인)**: Pi에서 사람 수를 0/1 존재 플래그로 변환 → Arduino에서 정지구간 색상 판별 → 두 조건을 결합해 정지 → 버튼 재출발.

```text
Pi: people_num != 0 → 1 (사람 있음), 아니면 0
Arduino: 정지구간 감지 && (Pi 사람 존재 플래그 == 1) → 정지
```

이 표현의 0/1 극성은 현재 복원에서 선택한 값이며, 최종 당시 코드의 극성은 미확인입니다.

**과거 문답에 남은 시험 조건식(역사적 기록, 최종 역할 아님):**

```python
color_condition = (r >= 4) or (r >= 2 * g) or (r >= 2 * b)
if button == 1:
    result = 1
elif (color_condition or people_num != 0) and button == 0:
    result = 0
else:
    result = previous_result
```

이 식은 Pi에서 색까지 판단하고 색상만으로 정지할 수 있어 사용자가 확인한 실제 최종 역할과 다릅니다. 과거 코드 기록은 [조건식 감사](docs/CONTROL_LOGIC_AUDIT.md)에 보존하며 현재 실행 코드에는 적용하지 않았습니다.

## 폴더 구성

```text
arduino/line_tracer/line_tracer.ino  Arduino 측 코드 복원
raspberry_pi/main.py                Pi 측 순차 처리와 제어 로직 복원
raspberry_pi/count_objects.py       Safe Watch의 TFLite 사람 검출 부분을 추출한 복원
raspberry_pi/models/               모델 가중치 미확보 안내
raspberry_pi/image/                런타임 이미지 경로 안내
tests/                             상태·사람 수 판정 테스트
simulation/                        하드웨어 없는 시나리오
docs/                              출처, 확정/추정 구분, 누락 사항
```


## 장치 간 흐름도 (역할 분담 교정 복원)

```mermaid
flowchart TD
  A[Raspberry Pi: 주행 중 반복 촬영] --> B[사람 수 검출]
  B --> C[Pi: 인원수 → 존재 여부 0/1]
  C --> D[Arduino: 사람 존재 신호 수신]
  E[Arduino: TCS34725 정지구간 감지] --> F{정지구간 AND 사람 존재?}
  D --> F
  F -- 예 --> G[Arduino: 정지·적재 대기]
  F -- 아니요 --> H[Arduino: IR 라인 추종 유지]
  G --> I[Arduino: 버튼 재출발]
```

주행 중 카메라가 사람을 먼 시야에서 먼저 인식하지만 **Pi는 정지구간을 판단하지 않습니다**. 사람 인식 결과의 **갱신 주기는 0.3초**로 확인됐습니다. Arduino가 해당 구간에 도착했을 때 최신 인식값을 사용해 정지하고, 버튼 재출발 뒤에는 **두 정지 조건을 모두 일시 무시**합니다. 최종 RGB 역치와 무시 기간은 미확정입니다.

## 추가 확인된 개발 단계의 차이

- **2023-11-24**에는 0/1 결과가 달라질 때만 전송하도록 요청했습니다. 현재 Pi 복원은 사람 존재 플래그를 **최초 1회와 변경 시** 송신합니다. 이 빈도가 최종 당시 코드와 동일한지는 미확인입니다.
- **2023-11-28**에는 `people_num`을 직접 전송하려는 별도의 **개발 실험**이 있었지만, 사용자가 확인한 실제 최종 구조에서는 사람 수를 Arduino에 넘기지 않았습니다. 당시 `int.encode()` 오류와 `bytes([data])`/Arduino `Serial.parseInt()` 형식 불일치는 시험 기록에 보존했습니다.
- **2023-11-16~17**에는 Uno 자체에 영상 AI를 넣으려던 시도가 있었지만 라이브러리 빌드 오류가 있었고, 실제 완성 프로젝트에서는 Pi가 인식을 담당한 것으로 구분했습니다.

[개발 대화의 날짜별 근거](docs/CHAT_HISTORY_AUDIT.md).

## 하드웨어 없이 실행 가능한 검증

```bash
python3 -m unittest discover -s tests -v
python3 simulation/trace.py
python3 -m py_compile raspberry_pi/main.py raspberry_pi/count_objects.py
```

실제 카메라/모델을 통한 추론에는 미확보된 `people_detect.tflite`와 해당 시스템의 라이브러리가 필요합니다. 하드웨어 구동·실측 성능은 검증하지 않았습니다.

## 확인된 부분과 가정한 부분

- 실제 경험으로 확인: 0.3초 사람 인식값 갱신, 라벨·테이프의 색상에 따른 센서 임계값 조정, 정지 후 버튼 전까지 유지, 재출발 후 사람·색상 두 정지 조건 모두 일시 무시, 실제 정지 시험 성공 및 지연 대응
- 사용자 직접 확인한 최종 역할: **Pi는 사람 존재 여부 0/1만 송신하고, Arduino는 TCS34725 정지구간과 결합하여 정지**, IR 주행·버튼 재출발 담당
- 추가 스케치에서 확인: IR 핀 7/8과 9600bps, 한 버전의 RGB 변환 예시, 색상/사람·버튼·통신 응답을 조합하려 했던 개발 과정
- 여전히 미확인: 최종 Arduino/Pi 원본 파일, 최종 RGB 역치·시리얼 개행·실제 상태 변화 송신 방식, 0.3초를 넘는 추론 지연 시 처리, 재출발 무시 시간(초), 당시 추출 함수 반환형
- 배제: 비동기 워커, 현대식 상태 관리자, HOG 대체 감지, 미확인 자동 안전정지 정책 등 후대에 추가했던 설계

자세한 구분은 [최종 역할 분담](docs/FINAL_ROLE_DIVISION.md), [확정·추정 목록](docs/CONFIRMED_VS_INFERRED.md), [처리 흐름·공백](docs/FLOW_AND_GAPS.md), [사람 감지·정지 영향 검증](docs/CONTROL_LOGIC_AUDIT.md)을 참고하세요.

## 정리 이력과 원본 출처

이 저장소는 **2023년 대화 충실 복원본 하나만 남긴 상태**입니다. 이전에 추가한 개선·재구성 코드 파일은 현재 브랜치에서 제거했으며 과거 Git 커밋 기록에만 남아 있습니다. 당시의 실제 라인트레이서 원본 파일을 찾았다는 뜻은 아닙니다.

Safe Watch 참조 코드: https://github.com/hsw-dotcom/safe-watch-crowd-monitoring/blob/main/src/python/count_objects.py

사람 검출 코드의 원래 기초에는 Evan Juras의 TensorFlow Lite 예제 코드가 사용되었습니다.

## 자동 오프라인 검증

[GitHub Actions — Offline reconstruction tests](https://github.com/hsw-dotcom/human-aware-line-follower/actions/workflows/offline-checks.yml)는 현재 **2026년 복원 코드**의 단위 테스트, 모의 시리얼 제어 흐름, Python 구문 검사를 수행합니다. 실기기 주행·사람 검출·제어 안정성을 검증하지 않습니다.
