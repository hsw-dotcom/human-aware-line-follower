# 라인트레이서 사람 감지 정지 기능 (2023.12) — 대화 기록 기반 보완판

> **원본 복구가 아니라, 사용자가 과거 대화에서 확정한 요구사항을 중심으로 재구성·보완한 코드입니다.**
> `RECONSTRUCTED / DIALOGUE-ENHANCED` · Arduino 및 Pi 실기기 미검증

## 무엇을 수행하는가

기존 Arduino IR 라인트레이서의 주행을 유지하고, 특정 바닥색 구간에서 Raspberry Pi 카메라로 사람 존재를 확인하여 정지하도록 연동합니다. Arduino는 `r:g:b:button`을 보내고, Pi는 `0`(정지) 또는 `1`(라인 추종 허용)을 회신합니다. 버튼은 재출발을 허용하며, 재출발 뒤 약 1~3초 동안 정지 조건을 무시합니다.

사용자의 당시 문답을 바탕으로 다음 규칙을 **그대로** 적용했습니다.

```python
color_condition = (r >= 4) or (r >= 2 * g) or (r >= 2 * b)
if button == 1:
    result = 1
elif (color_condition or people_num != 0) and button == 0:
    result = 0
else:
    result = previous_result
```

**주의:** 위 색상 판정식은 `r=g=b=0`일 때도 참입니다. 과거 식을 임의로 고치지 않았습니다. 실제 실험에서는 RGB 단위와 조도별 값을 꼭 측정해야 합니다.

## 디렉터리

- `arduino/line_tracer/line_tracer.ino`: 모터·IR·TCS34725·버튼·시리얼(원본 배선 일부만 확인)
- `raspberry_pi/line_tracer/`: 직렬 패킷, 판단 상태, 카메라, 사람 검출 대체기, 비동기 연동
- `raspberry_pi/config.example.ini`: 포트, 캡처간격, 재출발 무시 시간 설정 예제
- `tests/`: Python 단위테스트 및 인터페이스 검증
- `simulation/`: 외부 장치가 없는 전형적 진행 시연
- `docs/`: 대화에서 확인된 사항/추정 사항, 배선, 사용법, 검증 기록, 변경내역
- `original_source/`: 실제 원본 미확보 알림

## 실행

```bash
# 저장소 최상위 폴더에서 하드웨어 없는 테스트
python3 -m unittest discover -s tests -v
python3 simulation/demo.py

# Pi에서 실행 전 반드시 배선/라이브러리 확인
cp raspberry_pi/config.example.ini raspberry_pi/config.ini
cd raspberry_pi
python3 -m line_tracer.main --config config.ini
```

모터 바퀴를 공중에 띄운 상태에서 Arduino의 0/1 응답 및 방향을 먼저 검증하세요. 파일만으로 실제 장치의 안정적인 동작을 보장하지 않습니다.

## 중요: 기록 기반 구현과 새롭게 보완한 구현을 구분

**기록 기반:** 핀 3, PWM 5/6/9/10, IR HIGH/LOW 주행 진리표, `r:g:b:button`, 결과 `0/1`, `before.jpg` 저장 후 `count_objects.detect()` 호출, 색상·버튼·이전상태 판단식, 재출발 후 1~3초 무시, 거리 3~5m 인식 시험 진술.

**새 보완:** 시리얼에 정확히 개행으로 응답하는 처리, 오류 시 정지, 딜레이가 긴 사람 감지를 별도 스레드에서 처리, 이전 감지 결과 폐기, 통신 파싱 검증, 상태 테스트, 시뮬레이터.

**미확보/가정:** 실제 `.ino`·`.py` 원본, 사람 검출 모델 가중치, IR 연결 핀 2/4, USB 시리얼 9600bps, RGB 정규화, 각종 PWM·타임아웃 수치. 특히 `count_objects.py`의 HOG 대체 감지기는 **2023년 사용 모델이 아닙니다**.

기술적 유래와 제약 사항은 `docs/SOURCE_PROVENANCE.md`, `docs/DETAILED_BEHAVIOR.md`를 보세요.
