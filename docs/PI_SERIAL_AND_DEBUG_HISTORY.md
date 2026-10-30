# Raspberry Pi–Arduino 시리얼 시험 버전과 실제 오류

**사용자 최종 확인(2026-10-31): 실제 완성 시스템에서는 Pi가 사람 수를 0/1 존재 신호로 변환해 Arduino에 송신했고, Arduino는 TCS34725 정지구간과 결합해 정지했습니다.** 사람 수 직접 송신과 Pi가 RGB까지 판정한 코드는 **개발 실험**입니다. 당시 완성본의 전체 원문은 미확보입니다.

## 주요 통신 실험 3가지

| 실험 단계 | Pi 송신 | Arduino 수신 | 상태 |
|---|---|---|---|
| 사람 수 직접 송신 | `people_num` 정수 | `Serial.parseInt()`; 정수 0 이외면 정지 | 2023-11-28 **초기 시험**. 사용자 확인 최종 설계에는 미적용 |
| Pi가 RGB·버튼까지 판단해 결과 송신 | `result` 0 또는 1, 변경 시 전송 | Arduino의 0·1 분기 | 2023-11-24 **과거 문답의 다른 설계**, 최종 역할과 다름 |
| 현재 최종 역할 기반 복원 | Pi가 사람 존재만 ASCII `"0\n"` 또는 `"1\n"`로 최초·변경 시 송신 | Arduino는 `Serial.read()`로 사람 존재 신호 유지하고 색상 센서 자체 판정 | 2026년 복원 선택. Pi는 정지구간 판단하지 않음 |

### 2023-11-28 실제 오류: int에는 encode가 없음

사용자가 보여준 Pi 코드의 `ser.write(data.encode())`는 `data`가 정수인 `people_num`이면 `AttributeError: 'int' object has no attribute 'encode'`로 실패합니다.

후속 대화에서 ChatGPT가 `bytes([data])`를 제안했고 사용자가 해당 형태로 수정한 코드를 게시했습니다. 하지만 `bytes([2])`가 내보내는 값은 정수 2의 **원시 바이트 0x02**이며 텍스트 숫자 문자 `'2'`(ASCII 0x32)가 아닙니다. Arduino의 `Serial.parseInt()`는 숫자 문자(0x30~0x39)를 파싱하므로 이 두 코드를 **그대로 조합해 제대로 정지했다는 근거가 없습니다**. 사용자는 그 뒤 인원이 검출되는데도 Arduino가 멈추지 않았다고 보고했습니다.

전송 프로토콜을 맞춘다면 ASCII 숫자 전송 `ser.write(str(people_num).encode())` ↔ Arduino `Serial.parseInt()`처럼 텍스트/파싱 방식을 통일할 수 있으나, **이는 지금 확인한 해결 원리이지 당시 실제 적용한 최종 수정이라고 주장하지 않습니다.**

### 2023-11-24 사용자 요구: 결과가 달라졌을 때만 전송

```python
if current_result != previous_result:
    send_data_to_arduino(ser, current_result)
```

최종 실제 역할에서 Pi가 전송하는 0/1은 **사람 존재 여부**이며 RGB·버튼을 결합한 '모터 정지/주행 결과'가 아닙니다. 현 복원 Pi는 최초 검출 플래그를 한 번 보내고, 사람이 보이는지 여부가 변경될 때에만 다시 보냅니다. Arduino가 마지막 값을 보유하므로 이렇게 구현할 수 있지만 **원본 인식 결과의 갱신 간격은 0.3초, 이진 신호 극성은 0=없음/1=있음으로 사용자 확인됐습니다.** 다만 원본 시리얼 송신이 갱신 때마다 이루어졌는지 값 변화 시에만 이루어졌는지는 미확인입니다.

### 초기 시험에서 확인된 기타 오류

- 2023-11-21: Pi에 `/dev/ttyACM0` 장치가 보이지 않는 `SerialException` 및 USB 포트 연결 점검
- `netifaces`, `matplotlib`, `tflite_runtime` 모듈 누락, 오래된 `cp37`/ARM TFLite wheel 플랫폼 비호환
- 2023-11-23: `before.jpg` 읽기 실패에 따른 OpenCV `cvtColor(... !_src.empty())` 오류; `get_frame(ip)` 저장 위치와 검출기가 읽는 위치 불일치 가능
- 2023-11-25: `cv2.imwrite`에서 빈 프레임으로 `!_img.empty()` 오류
- 2023-11-21: Pi `main.py`의 `IndentationError`도 개발 중 나타남
- 2023-11-16~17: Arduino Uno에 TFLite Micro/Teachable Machine 예제 적용 시 `cstdarg`, `cstddef`, `tensorflow/lite/c/common.h` 등 누락으로 컴파일 실패. **최종 프로젝트에서 Uno 자체가 TensorFlow 추론을 수행했다는 기록은 아님**.

각 오류는 개발 과정에서 나타난 것이며, 최종 성공 버전에서도 동일하게 발생했다는 의미는 아닙니다.
