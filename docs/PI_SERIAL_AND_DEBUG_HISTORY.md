# Raspberry Pi–Arduino 시리얼 시험 버전과 실제 오류

이 문서는 2023년 각 대화에서 등장한 **서로 호환되지 않는 통신 단계**를 구분합니다. GitHub의 실행용 Pi/Arduino 복원은 당시 최종 동작 원본이 아닙니다.

## 주요 통신 실험 3가지

| 실험 단계 | Pi 송신 | Arduino 수신 | 상태 |
|---|---|---|---|
| 사람 수 직접 송신 | `people_num` 정수 | `Serial.parseInt()`; 정수 0 이외면 정지 | 2023-11-28 시험. 최종 성공 여부 미확인 |
| 제어 결과 송신 | `result` 0 또는 1, 변경할 때만 전송 | Arduino의 RGB/버튼 전송 코드에 0·1 분기 | 2023-11-24 **사용자 요구**; 정확한 마지막 송수신 코드 쌍 미확보 |
| 현재 통합 복원 | ASCII `"0\n"` 또는 `"1\n"`를 매 입력에 회신 | `Serial.readStringUntil('\n')` 사용 | 2026년 실행용 복원 선택. 결과 극성은 버전에 따라 다름 |

### 2023-11-28 실제 오류: int에는 encode가 없음

사용자가 보여준 Pi 코드의 `ser.write(data.encode())`는 `data`가 정수인 `people_num`이면 `AttributeError: 'int' object has no attribute 'encode'`로 실패합니다.

후속 대화에서 ChatGPT가 `bytes([data])`를 제안했고 사용자가 해당 형태로 수정한 코드를 게시했습니다. 하지만 `bytes([2])`가 내보내는 값은 정수 2의 **원시 바이트 0x02**이며 텍스트 숫자 문자 `'2'`(ASCII 0x32)가 아닙니다. Arduino의 `Serial.parseInt()`는 숫자 문자(0x30~0x39)를 파싱하므로 이 두 코드를 **그대로 조합해 제대로 정지했다는 근거가 없습니다**. 사용자는 그 뒤 인원이 검출되는데도 Arduino가 멈추지 않았다고 보고했습니다.

전송 프로토콜을 맞춘다면 ASCII 숫자 전송 `ser.write(str(people_num).encode())` ↔ Arduino `Serial.parseInt()`처럼 텍스트/파싱 방식을 통일할 수 있으나, **이는 지금 확인한 해결 원리이지 당시 실제 적용한 최종 수정이라고 주장하지 않습니다.**

### 2023-11-24 사용자 요구: 결과가 바뀌었을 때만 전송

```python
if current_result != previous_result:
    send_data_to_arduino(ser, current_result)
```

이는 사용자의 분명한 개발 요구입니다. 현재 실행용 복원 `raspberry_pi/main.py`는 **매 요청에 응답하는 형태**입니다. 함께 복원된 Arduino가 매 루프에서 `readStringUntil('\n')`를 기다리므로 변경 시에만 송신하도록 Pi만 바꾸면 **Arduino가 수신 대기 중 멈추거나 지연될 수 있습니다**. 이 요구는 역사적 기록으로 남기고 실제 최종 통신 프로토콜로 단정하지 않았습니다.

### 초기 시험에서 확인된 기타 오류

- 2023-11-21: Pi에 `/dev/ttyACM0` 장치가 보이지 않는 `SerialException` 및 USB 포트 연결 점검
- `netifaces`, `matplotlib`, `tflite_runtime` 모듈 누락, 오래된 `cp37`/ARM TFLite wheel 플랫폼 비호환
- 2023-11-23: `before.jpg` 읽기 실패에 따른 OpenCV `cvtColor(... !_src.empty())` 오류; `get_frame(ip)` 저장 위치와 검출기가 읽는 위치 불일치 가능
- 2023-11-25: `cv2.imwrite`에서 빈 프레임으로 `!_img.empty()` 오류
- 2023-11-21: Pi `main.py`의 `IndentationError`도 개발 중 나타남
- 2023-11-16~17: Arduino Uno에 TFLite Micro/Teachable Machine 예제 적용 시 `cstdarg`, `cstddef`, `tensorflow/lite/c/common.h` 등 누락으로 컴파일 실패. **최종 프로젝트에서 Uno 자체가 TensorFlow 추론을 수행했다는 기록은 아님**.

각 오류는 개발 과정에서 나타난 것이며, 최종 성공 버전에서도 동일하게 발생했다는 의미는 아닙니다.
