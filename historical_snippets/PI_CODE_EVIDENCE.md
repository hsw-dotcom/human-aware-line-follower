# Pi 관련 보존 코드 및 원문 출처

- **`02_serial_echo_test.py`** — 사용자가 제공한 Raspberry Pi 시리얼 송수신 시험 코드의 원문. `/dev/ttyACM0`, `9600`, `ser.readline()`, `ser.write()` 등을 포함하며 최종 통합 제어 코드가 아닙니다.
- **Arduino `.ino` 여러 버전** — 각 버전마다 Pi가 송수신해야 할 메시지 형태와 0/1 의미가 다릅니다. [Arduino 비교 문서](../docs/USER_SUPPLIED_ARDUINO_VERSIONS.md).
- **2023-11-23~24 Pi `main.py` 기록** — `/home/pi/project/main.py`, `get_ip()`, `get_frame(ip)`, `count_object()`, `count_objects.detect()`, `send_data_to_arduino(...)` 등의 실제 사용자 코드 흔적이 남지만 전체 파일은 확보되지 않았습니다. 해당 파일을 만들어 '원본'으로 표시하지 않습니다.
- **Safe Watch 원본 검출 코드** — [별도 GitHub 저장소의 `src/python/count_objects.py`](https://github.com/hsw-dotcom/safe-watch-crowd-monitoring/blob/main/src/python/count_objects.py)에서 확인 가능. 라인트레이서에서는 필요한 인식 기능만 추출했다는 사용자 설명을 따릅니다.

이 폴더는 역사적 참고 자료입니다. 현재 정리된 Pi 코드의 위치와 불확실성은 [Pi 코드 분류](../docs/PI_CODE_VERSIONS.md)에서 확인하세요.
