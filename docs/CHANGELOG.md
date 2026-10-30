# 대화 기반 보완 변경 사항

- 2023년 설명에 나온 Arduino IR 4가지 분기, PWM 핀 4개, 버튼 입력, RGB 직렬 메시지 유지.
- Pi 최종 규칙 (버튼 우선, 색/사람 정지, 이전 결과 유지) 별도 모듈로 명시.
- `VisionWorker` 추가: 오래 걸리는 `count_objects.detect()`를 워커에서 수행, Arduino 응답 지연 완화.
- `Coordinator` 추가: 과거 감지 결과를 재출발할 때 무효화하고 진입 중 안전하게 정지.
- `detector_adapter` 추가: 검출기 반환값의 알려지지 않은 형식에 대비한 정수/2-튜플 처리.
- Arduino의 응답 처리: 완성된 `0\n` / `1\n`만 허용, 오류나 미응답은 정지.
- `tests/test_vision.py`, `tests/test_coordinator.py`, `tests/test_trace.py` 추가.
- `simulation/demo.py` 추가 및 장치 없이 진행 결과 확인.
- 과거 설명과 새 가정 및 엔지니어링 보완 사항을 문서에서 분리.

> 변경 전 ZIP과 신규 ZIP의 어느 소스도 실제 2023년 원본으로 검증된 것은 아닙니다.

## 2026-10-31 — Safe Watch 기능 재사용 출처 확정

- 사용자 추가 설명: 라인트레이서의 사람 인식 라이브러리는 Safe Watch에서 필요한 사람 인식 기능만 추출해 재사용한 것.
- 이전 OpenCV HOG **임의 대체** 코드 제거; Safe Watch `src/python/count_objects.py`에서 확인된 TFLite 사람 수 계산 로직으로 재복원.
- Safe Watch 사람 클래스 0, 신뢰도 0.2, 640×640, TF1/TF2 출력 분기를 보존.
- 실제 모델 파일 및 라인트레이서 당시 추출본은 아직 미확보. 학습·정확도 개선을 새 성과로 주장하지 않음.
- `docs/SAFEBWATCH_REUSE.md`, `raspberry_pi/models/README.md`, `tests/test_count_objects.py` 추가.
