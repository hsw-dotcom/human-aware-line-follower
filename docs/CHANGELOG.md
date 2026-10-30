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
