# 사람 인식 기반 라인트레이서 (2023.12) — 대화 충실 복원

> **당시 원본 소스코드 전문이 복구된 것은 아닙니다.** 2023년 대화에서 확인된 값과
> Safe Watch에 실제 남은 사람 인식 코드를 최우선으로 사용한 **역사적 동작 복원**입니다.
> 하드웨어가 없다는 전제에서 문법, 입력·출력 및 상태 전이만 점검합니다.

## 이번 복원의 기준

- **대화에서 확인된 사실:** Arduino 기반 라인 추종과 색상 구간 감지, Raspberry Pi의 카메라
  촬영 및 사람 인식, `r:g:b:button` ↔ `result(0/1)`, PWM 핀 5/6/9/10,
  버튼 핀 3, IR 조건 HH/LH/HL/LL, 최종 Python 판단식, `before.jpg` 저장 후
  `count_objects.detect()` 호출, 재출발 후 1~3초 감지 무시.
- **다른 프로젝트에서 확인 가능한 원본:** Safe Watch의 `src/python/count_objects.py`
  (TensorFlow Lite, `people_detect.tflite`, 사람 클래스 0, 신뢰도 0.2, 640x640 RGB 입력).
- **미확인:** 라인트레이서 원본 `.ino`와 Python 전문, 당시 RGB값 변환식,
  IR 센서 입력 핀, 시리얼 속도, 카메라 색 형식, 재출발 무시 시간의 최종값,
  라인트레이서용으로 추출한 `count_objects.py`의 정확한 반환형, 모델 가중치.

## 코드 구성 (작고 직관적인 2023년식 구조)

```text
arduino/line_tracer/line_tracer.ino   # 센서, 버튼, 모터, 시리얼
raspberry_pi/main.py                 # 한 루프에서 시리얼 수신 → 필요 시 촬영 → 판정 → 회신
raspberry_pi/count_objects.py        # Safe Watch 사람 인식만 추출한 TFLite 함수
raspberry_pi/models/README.md       # 모델 파일 미확보 설명
raspberry_pi/image/README.md        # before.jpg 런타임 파일 설명
tests/                                # 대화로 확인된 판단 규칙 테스트
docs/                                 # 출처, 확실성, 원본 대비 차이
```

```python
# 당시 마지막으로 정리한 판단식 (표현 구조만 최소화)
if button == 1:
    result = 1
elif (r >= 4 or r >= 2*g or r >= 2*b or people_num != 0) and button == 0:
    result = 0
else:
    result = previous_result
```

**중요:** 위 색 조건의 `r>=2*g` 또는 `r>=2*b`는 `r=g=b=0`에서도 참입니다.
정확한 RGB 단위·비율 변환은 대화로 확인할 수 없어 임의로 확정하지 않습니다.
색 조건이 참이면 사람 수와 무관하게 정지하므로, 지정 구간에서 사람을 확인하던 의도와
완전히 일치한다고 단정할 수 없습니다. **식 자체는 임의 수정하지 않았습니다.**

## 하드웨어 없이 확인

```bash
python3 -m unittest discover -s tests -v
python3 simulation/trace.py
python3 -m py_compile raspberry_pi/main.py raspberry_pi/count_objects.py
```

이 저장소의 기존 비동기·안전성 강화 코드는 `modernized` 계열로 취급하십시오. 이번 복원본에는
`VisionWorker`, `Coordinator`, OpenCV HOG 검출기, 오류-정지 정책 등 당시 확인되지 않은
설계 변경을 넣지 않았습니다. 개발 사실과 후대 보완을 혼동하지 않기 위한 결정입니다.

## 관련 공개 기록

- Safe Watch 사람 감지 원본: https://github.com/hsw-dotcom/safe-watch-crowd-monitoring/blob/main/src/python/count_objects.py
- 라인트레이서 저장소: https://github.com/hsw-dotcom/human-aware-line-follower
