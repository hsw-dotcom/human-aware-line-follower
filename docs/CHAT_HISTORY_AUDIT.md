# 전체 대화 재대조 — 라인트레이서 2023년 개발기록 근거표

> 2026-10-31 프로젝트 관련 대화 기록·현재 사용자 설명·GitHub 파일을 다시 교차 검토한 결과입니다.
> **모든 실제 2023년 소스 전문을 회수했다는 뜻은 아닙니다.**
> 출처는 사용자 입력 대화, 사용자 제공 코드, ChatGPT 제안, 사용자 회고를 엄격히 분리합니다.
> 각 날짜는 기록 발견 시점/사용자 메시지 날짜이며 최종 설치 일자는 아닙니다.

## 확인된 개발 흐름 및 기존 문서에 부족했던 내용

| 시점 | 구체적 사실/요청 | 기록의 성격 | 저장소 반영 |
|---|---|---|---|
| 2023-11-16~17 | Arduino Uno에서 Teachable Machine/TFLite Micro·ESP32용 라이브러리 적용 시도, `cstdarg`, `cstddef`, `tensorflow/lite/c/common.h` 누락 컴파일 오류 | **초기 시험 및 실패**. Uno에서 영상 AI 성공 증거 없음 | 최종 구현과 분리 기록 |
| 2023-11-21 | Pi에서 `/dev/ttyACM0` USB 시리얼·9600bps 시험, `netifaces`·`matplotlib`·`tflite_runtime` 의존성 설치 및 포트 관련 오류 | 개발 환경 디버깅 | [오류 기록](PI_SERIAL_AND_DEBUG_HISTORY.md) |
| 2023-11-21 | 별도 `pi.jpg` 파일 경로로 영상 저장 시험. `before.jpg`/Safe Watch 검출기의 이미지 경로와 차이 | 초기 스냅샷 테스트 | 해당 경로들을 최종 경로로 혼합하지 않음 |
| 2023-11-21~23 | Arduino 모터 PWM 5·6·9·10, IR 7·8, 버튼 D3, speed 255, Serial 9600, TCS34725 50ms/4X; 적색 조건 `r>=5`, 인원수 `>=1` 또는 `2` 시험 | 사용자 제공 개발 스케치·조건 변경 | [기존 보존 스케치](USER_SUPPLIED_ARDUINO_VERSIONS.md)와 연결 |
| 2023-11-23 | Pi 사용자 코드에서 `get_ip()`(wlan0)·`get_frame(ip)`(MJPEG 프레임)·`count_objects.detect()` 호출. `/home/pi/project/before.jpg` 저장 시도, 이미지 경로 불일치로 OpenCV 오류 | 사용자 코드 및 실제 traceback | 현재 복원에는 `get_ip/get_frame` 형태 반영. **Picamera2는 별도 stream.py 등에서 시험된 카메라 계층**으로 구분; 메인 소스와 혼합하지 않음 |
| 2023-11-23~24 | 사람 인식은 `get_frame`→`count_object`로 먼저 진행, 이후 Arduino 색상·버튼 통신 판정 | 사용자 코드 부분 확인 | 실행용 복원의 촬영 순서를 우선 근거로 반영 |
| 2023-11-23~24 | `r:g:b:button` 포맷, 색 조건 `r>=4 or r>=2*g or r>=2*b`, 버튼 입력과 `previous_result`; 과거 문답에는 `색 OR 사람` 조건 기록 | 대화 속 판단식 | 원문 보존, 실제 목적과 충돌을 명시 |
| **2023-11-24** | Arduino에 RGB/사람 수 전체가 아니라 **`result` 값만** 보낼 것, **`current_result != previous_result`인 경우에만 전송**할 것 요구 | 사용자 명시 요구 | [통신 버전 차이](PI_SERIAL_AND_DEBUG_HISTORY.md). 현 실행용 복원에 무비판 적용하지 않음 |
| 2023-11-24 | Arduino TCS34725 `red:green:blue:button` 송신; 예시 RGB `2:1:1` 관련 검토 | 사용자 제공 스케치·데이터 | 구간 색 조건의 RGB 스케일 미확정으로 분리 |
| 2023-11-25 | 라인트레이싱은 **계속 주행**하고 통신에 필요한 조건값만 **약 0.3초 간격으로 갱신** | 사용자 직접 설명 | 주행 자체를 300ms마다 정지한다고 해석하지 않음 |
| **2023-11-28** | Pi에서 `people_num` 정수를 `ser.write(data.encode())`로 전송하려다 `AttributeError` 발생; `bytes([data])` 전송안으로 바꿔 실험 | 사용자 코드·오류 및 제안·후속 수정 | **raw byte vs `Serial.parseInt()` 불일치** 설명 |
| 2023-11-28 | Arduino `receivedNumber != 0`이면 정지하는 코드, 버튼·`moving` 상태와 300ms 통신 확인 실험. 일부 코드가 수신 뒤에도 정지하지 않는 문제 보고 | 사용자 스케치·시험 피드백 | [Arduino 개발 버전 문서](USER_SUPPLIED_ARDUINO_VERSIONS.md) |
| **2026-10-31 사용자 재확인** | 멀리서 사람을 먼저 감지하고, **색상 센서가 정지구간을 감지하는 순간 두 조건을 결합해 정지**; 적재 후 버튼 재출발 | 사용자 실제 동작 회고 | [촬영 시점 근거](CAPTURE_TIMING_EVIDENCE.md), 현 Pi 복원 |

## 남아 있는 불확실성

1. 2023년 **최종 Arduino/Pi 파일 쌍** 전문 및 최종 채택 시점.
2. `r:g:b:button` 기반 0/1 통신과 `people_num` 직접 전송 시험 중 어떤 버전이 실장 최종본이었는지.
3. 색상 정지구간 표시와 '먼 시야'에서 인식된 사람 수가 정확히 같은 작업 위치를 가리키도록 연결한 방식(시야각·ROI·검출 결과 유지 주기).
4. `before.jpg`, `image/before.jpg`, `image/pi.jpg` 등 서로 다른 시험 경로의 최종 선택.
5. 정확한 정지 구간·조기 인식 시작 위치, 재출발 후 색 무시 시간(1~3초), 지연 시간과 반복 성공률.

최종 실장 성공 자체는 사용자가 직접 확인한 개발 경험으로 기록하되, 각 시험 코드가 그 성공한 전체 코드라고 인증하지 않습니다.
