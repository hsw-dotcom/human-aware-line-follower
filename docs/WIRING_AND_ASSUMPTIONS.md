# 배선 표 (확인된 값 / 추정값)

| 위치 | 값 | 확실성 |
|---|---|---|
| BUTTON_PIN | D3 / INPUT_PULLUP | 대화 확인 |
| LmotorCW | PWM D5 | 대화 확인 |
| LmotorCCW | PWM D6 | 대화 확인 |
| RmotorCW | PWM D9 | 대화 확인 |
| RmotorCCW | PWM D10 | 대화 확인 |
| IRL | D2 | **추정** |
| IRR | D4 | **추정** |
| TCS34725 | I2C / Adafruit library | 부품 확인·구체 연결 추정 |
| Serial | 9600 bps / LF | **추정** |
| Motor driver | PWM·방향 신호 방식 | **추정** |
| RGB 수치 | raw RGB / sum × 10 (정수 버림) | **추정** |
| 정상/회전 PWM | 150/135 | **추정** |

IR HIGH/LOW 주행 규칙은 확인되지만 모터의 CW/CCW 극성이 다를 수 있습니다. 바퀴를 들어 전원·전방/좌우 방향과 센서 논리를 각각 확인한 다음 PWM을 올리세요.

'IRL=2, IRR=4'는 실제 핀도면에서 증명되지 않았습니다. 드라이버 전원, 풀업, 센서 I2C 레벨(3.3/5V), Arduino 보드 종류 역시 개별 확인이 필요합니다.
