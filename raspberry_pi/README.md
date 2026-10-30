# Raspberry Pi 코드 안내

**이 폴더의 두 Python 파일은 실제 2023년 파일 전문이 아니라 대화 기록으로 재구성한 코드입니다.** 당시 실사용 Arduino와 통신한 최종 Pi 소스는 아직 확인되지 않았습니다.

| 파일 | 내용 |
|---|---|
| [`main.py`](main.py) | Arduino 패킷 수신·이미지 저장·**검사 구간에 대기자 있을 때만 정지**하는 판단과 회신 |
| [`count_objects.py`](count_objects.py) | Safe Watch 사람 검출 부분에서 추린 TFLite 사람 수 판정 |
| [`models/README.md`](models/README.md) | 모델 파일 미확보 안내 |
| [`image/README.md`](image/README.md) | 실행 시 저장되는 프레임 파일 경로 |
| [`requirements-reference.txt`](requirements-reference.txt) | 참고용 의존성, 당시 버전 불명 |

**실제로 제공된 Pi 시리얼 테스트 원문**은 [`historical_snippets/02_serial_echo_test.py`](../historical_snippets/02_serial_echo_test.py)에 있고, 당시 원본 사람 검출 라이브러리의 출처는 [Safe Watch `count_objects.py`](https://github.com/hsw-dotcom/safe-watch-crowd-monitoring/blob/main/src/python/count_objects.py)입니다.

[Pi 코드별 출처·개발 순서·충돌 사항](../docs/PI_CODE_VERSIONS.md) · [검출 재사용 근거](../docs/DETECTOR_REUSE_EVIDENCE.md) · [제어상 한계](../docs/CONTROL_LOGIC_AUDIT.md)

**2023년 11월 23~24일 대화에서 Pi의 반복 프레임 저장·사람 검출이 색상 판정보다 앞서 실행된 흔적이 있습니다.** 현재 `main.py`는 매 반복 `sample_people()`을 실행해 최신 사람 수를 구하고, 그 후 RGB/버튼을 받아 정지 여부를 판단합니다. [시점 근거](../docs/CAPTURE_TIMING_EVIDENCE.md).

과거 문답에 등장한 `색 OR 사람` 판단식은 [제어식 문서](../docs/CONTROL_LOGIC_AUDIT.md)에 역사적 기록으로 보존했으며, 이 폴더의 실행용 복원본은 사용자 목적에 따라 `색 AND 사람`으로 교정했습니다.

**현재 컴퓨터에 하드웨어가 없으므로** 테스트 범위는 문법·단위 테스트·시뮬레이션이며, 실제 2023년 하드웨어 시험을 재현한 것은 아닙니다.
