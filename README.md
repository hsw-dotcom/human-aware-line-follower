# 사람 인식 기반 라인트레이서 — 2023년 12월 대화 충실 복원본

> **2023년 당시 작성한 소스코드 원본 전문이 아닙니다.**
> 프로젝트 관련 과거 대화에서 확정된 코드·제어 규칙과 Safe Watch의 확인 가능한 사람 검출 소스를 근거로 복원한 최종 정리본입니다.
> 하드웨어가 없으므로 코드·논리·입출력 시뮬레이션만 검토합니다.


## 새로 제출된 실제 개발 스케치 6종 (중요한 추가 자료)

사용자가 Arduino 개발 과정에서 작성한 **여섯 개의 서로 다른 코드 텍스트**를 새로 제출했습니다. [스케치 보존 폴더](historical_snippets/)와 [버전별 검증 기록](docs/USER_SUPPLIED_ARDUINO_VERSIONS.md)에 **파일별로 원문 형태로 보관**했습니다.

- 제공된 스케치 여러 버전에서 **IR 센서 핀 7·8, PWM 5·6·9·10, 버튼 핀 3, 시리얼 9600bps**가 확인됩니다. 과거 코드 복원 시 임의로 가정했던 IR 핀 2·4보다 이 추가 증거를 우선합니다.
- RGB 원시값을 `map(raw, 0, 21504, 0, 1025)`로 변환하고, **300ms마다 통신을 검사하거나 1초마다 색상을 검사**하는 시험 버전이 있습니다. 이것을 최종 성능으로 단정하지는 않습니다.
- 시리얼 메시지 형식·`0/1`의 의미가 버전마다 달라 **기존 복원본의 `r:g:b:button` 계약이 유일한 최종 프로토콜이었다고 단정할 수 없습니다.**
- 마지막 제출 스케치에는 300ms 통신 검사에서 `lastCommunicationTime` 갱신 직후 100ms 경과를 검사하는 **실행되지 않는 분기**가 있습니다. 원문 수정 없이 기록했습니다.

**아래 통합 복원 코드(`arduino/line_tracer/line_tracer.ino`, `raspberry_pi/main.py`)는 원본 스케치와 별개입니다.** 어떤 스케치를 최종 실기기에 사용했는지는 아직 미확인입니다.

## 프로젝트 개요

기존 Arduino 라인트레이서에 Raspberry Pi 카메라를 연계해 **작업 구간의 사람 존재에 따라 정지시키려 한 2023년 과제**입니다. 현재 공개된 소스는 2023년 원문이 아닌 대화 기반 복원본이며, 실제 사람 감지가 정지 신호를 결정했는지는 별도 확인이 필요합니다.

- **Arduino**: IR 센서 라인 추종, TCS34725 색상 판별, 버튼, PWM 모터 제어
- **Raspberry Pi**: 카메라 프레임을 `before.jpg`로 저장하고 `count_objects.detect()`로 인원 확인
- **시리얼**: Arduino → Pi `r:g:b:button`, Pi → Arduino `0`(정지) / `1`(주행 허용)
- **재출발**: 버튼 입력 시 1을 회신, 이후 1~3초의 감지 무시 구간을 두도록 실험
- **사람 인식**: 별도 모델을 학습한 것이 아니라 Safe Watch의 TensorFlow Lite 사람 검출 기능을 필요한 부분만 추려서 재사용


## 2023년 코드 재사용·통신 개발 화면

**Safe Watch의 객체 검출 코드를 추출해 라인트레이서에 사람 인식 기능을 적용하는 과정**의 화면들입니다. 당시 개발 흐름을 보여주는 자료이며, 최종 라인트레이서의 자동 정지 성공률이나 시연 결과는 아닙니다.

![기존 검출 코드 재사용 테스트 1 — 인물 영역 익명화](assets/2023_detector_reuse_test_redacted_1.jpg)

![기존 검출 코드 재사용 테스트 2 — 인물 영역 익명화](assets/2023_detector_reuse_test_redacted_2.jpg)

![Arduino–Raspberry Pi 시리얼 통신 시험 — 접속정보와 대화내용 가림](assets/2023_serial_test_redacted.jpg)

[화면별 근거와 해석 범위](docs/DETECTOR_REUSE_EVIDENCE.md)

## 확인된 핵심 판단식

```python
color_condition = (r >= 4) or (r >= 2 * g) or (r >= 2 * b)
if button == 1:
    result = 1
elif (color_condition or people_num != 0) and button == 0:
    result = 0
else:
    result = previous_result
```

**검증상 중요한 한계:** 위 조건은 `r=g=b=0`에서도 참입니다. 또한 **현재 복원본은 색상 조건이 참일 때만 사람 탐지를 호출하는데 그 색상 조건만으로 이미 정지(0)하기 때문에, 사람 감지 결과가 실제 반환값을 바꾸지 않습니다.** 이 문제가 2023년 당시 최종 프로그램에도 있었는지는 원본 미확보로 불명입니다. 제어식을 `AND`로 임의 변경하지 않았습니다. [판정 경로 검증](docs/CONTROL_LOGIC_AUDIT.md).

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


## 장치 간 흐름도 (2026년 기록 기반 복원)

```mermaid
flowchart TD
  A[Arduino IR 센서·색상 센서·버튼] --> B[시리얼 r:g:b:button 전송]
  B --> C[Raspberry Pi 수신]
  C --> D{색상 조건?}
  D -- 참 --> E[카메라 프레임·사람 검출]
  D -- 거짓 --> F[사람 검출 없이 이전 상태]
  E --> G[버튼·색상·사람 조건으로 0/1 판단]
  F --> G
  G --> H[시리얼 0 또는 1 회신]
  H --> I[Arduino 정지 또는 라인 추종]
```

**그림은 현재 복원 코드의 호출 흐름을 단순화한 것**이며, 당시 카메라 호출 시점은 미확인입니다. 특히 색상 조건이 참일 때 사람 수와 관계없이 정지되는 문제는 [검증 문서](docs/CONTROL_LOGIC_AUDIT.md)를 참고하세요.

## 하드웨어 없이 실행 가능한 검증

```bash
python3 -m unittest discover -s tests -v
python3 simulation/trace.py
python3 -m py_compile raspberry_pi/main.py raspberry_pi/count_objects.py
```

실제 카메라/모델을 통한 추론에는 미확보된 `people_detect.tflite`와 해당 시스템의 라이브러리가 필요합니다. 하드웨어 구동·실측 성능은 검증하지 않았습니다.

## 확인된 부분과 가정한 부분

- 확정: 모터 PWM 핀 5/6/9/10, 버튼 핀 3, IR 입력 조합별 주행, RGB 시리얼 포맷, 최종 판단식, Safe Watch 사람 인식 기능 재사용
- 추가 스케치에서 확인: IR 핀 7/8과 9600bps, 한 버전의 RGB 변환 예시, 색상/사람·버튼·통신 응답을 조합하려 했던 개발 과정
- 여전히 추정: **최종 채택**된 IR 배선·RGB 스케일·0/1 회신의 의미·개행 방식·장치 경로, 카메라 호출 시점, 재출발 무시의 정확한 최종 시간, 당시 추출 함수의 반환값
- 배제: 비동기 워커, 현대식 상태 관리자, HOG 대체 감지, 미확인 자동 안전정지 정책 등 후대에 추가했던 설계

자세한 구분은 [확정·추정 목록](docs/CONFIRMED_VS_INFERRED.md), [처리 흐름·공백](docs/FLOW_AND_GAPS.md), [사람 감지·정지 영향 검증](docs/CONTROL_LOGIC_AUDIT.md)을 참고하세요.

## 정리 이력과 원본 출처

이 저장소는 **2023년 대화 충실 복원본 하나만 남긴 상태**입니다. 이전에 추가한 개선·재구성 코드 파일은 현재 브랜치에서 제거했으며 과거 Git 커밋 기록에만 남아 있습니다. 당시의 실제 라인트레이서 원본 파일을 찾았다는 뜻은 아닙니다.

Safe Watch 참조 코드: https://github.com/hsw-dotcom/safe-watch-crowd-monitoring/blob/main/src/python/count_objects.py

사람 검출 코드의 원래 기초에는 Evan Juras의 TensorFlow Lite 예제 코드가 사용되었습니다.

## 자동 오프라인 검증

[GitHub Actions — Offline reconstruction tests](https://github.com/hsw-dotcom/human-aware-line-follower/actions/workflows/offline-checks.yml)는 현재 **2026년 복원 코드**의 단위 테스트, 모의 시리얼 제어 흐름, Python 구문 검사를 수행합니다. 실기기 주행·사람 검출·제어 안정성을 검증하지 않습니다.
