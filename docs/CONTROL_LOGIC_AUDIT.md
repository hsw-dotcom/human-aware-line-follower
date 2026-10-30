# 정지 판단 로직 — Arduino 최종 역할 교정

## 최종 역할 (2026-10-31 사용자 직접 확인)

**Raspberry Pi는 사람 존재 여부 0/1을 계산·전송하고, Arduino가 정지구간을 감지해 정지 여부를 결정했습니다.** Pi는 정지구간 RGB를 판단하지 않았고, Arduino로 사람 수를 전달하지 않았습니다.

| Arduino 정지구간 | Pi의 사람 존재 신호 | 정상 주행 중 동작 |
|---|---|---|
| 아니요 | 0 | 계속 주행 |
| 아니요 | 1 | 계속 주행 |
| 예 | 0 | 계속 주행 |
| 예 | 1 | **정지·적재 대기** |

정지 후에는 버튼을 누르기 전까지 상태를 유지하고, 적재 후 일정 시간 정지구간 조건을 무시하고 재출발합니다.

## 예전 대화의 Pi 조건식은 최종 구현이 아님

```python
color_condition = (r >= 4 or r >= 2*g or r >= 2*b)
if button == 1:
    result = 1
elif (color_condition == 1 or people_num != 0) and button == 0:
    result = 0
else:
    result = previous_result
```

이 조건은 Pi에서 RGB와 버튼까지 판단하는 초기 논의 기록입니다. 색상만으로도 정지해 사용자 최종 목적과 다르므로 **원형을 기록으로 보존하지만 현재 실행 코드에는 사용하지 않습니다**.

## 현재 2026년 복원 동작

```text
Pi:  people_present = (people_num != 0) → 0/1 송신
Arduino: if stop_zone and people_present: stopped = true
Arduino: if stopped: stopMotor()
Arduino: 버튼으로 stopped 해제하고 정지구간 무시 시작
```

이 예시는 Pi 플래그 **1=사람 있음**이라는 임시 극성을 채택했습니다. 실제 2023년 원문 파일에서 부호를 독립 검증한 것은 아닙니다.

현재 Arduino 복원은 개발 스케치 01의 `r>=5` 색상 시험 조건과 1~3초 범위 중 2초를 사용합니다. 정확한 최종 역치, 피치 방향 센서값·RGB 스케일·색 영역·사람 검출 데이터 유지 시간은 미확인입니다.

[역할 분담](FINAL_ROLE_DIVISION.md) · [개발 스케치](USER_SUPPLIED_ARDUINO_VERSIONS.md).
