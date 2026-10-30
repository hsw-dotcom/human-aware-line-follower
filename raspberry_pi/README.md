# Raspberry Pi 코드 안내

**이 폴더의 두 Python 파일은 실제 2023년 파일 전문이 아니라 대화 기록으로 재구성한 코드입니다.** 당시 실사용 Arduino와 통신한 최종 Pi 소스는 아직 확인되지 않았습니다.

| 파일 | 내용 |
|---|---|
| [`main.py`](main.py) | Arduino 패킷 수신, 이미지 저장, 사람 검출 결과의 0/1 판단과 회신 |
| [`count_objects.py`](count_objects.py) | Safe Watch 사람 검출 부분에서 추린 TFLite 사람 수 판정 |
| [`models/README.md`](models/README.md) | 모델 파일 미확보 안내 |
| [`image/README.md`](image/README.md) | 실행 시 저장되는 프레임 파일 경로 |
| [`requirements-reference.txt`](requirements-reference.txt) | 참고용 의존성, 당시 버전 불명 |

**실제로 제공된 Pi 시리얼 테스트 원문**은 [`historical_snippets/02_serial_echo_test.py`](../historical_snippets/02_serial_echo_test.py)에 있고, 당시 원본 사람 검출 라이브러리의 출처는 [Safe Watch `count_objects.py`](https://github.com/hsw-dotcom/safe-watch-crowd-monitoring/blob/main/src/python/count_objects.py)입니다.

[Pi 코드별 출처·개발 순서·충돌 사항](../docs/PI_CODE_VERSIONS.md) · [검출 재사용 근거](../docs/DETECTOR_REUSE_EVIDENCE.md) · [제어상 한계](../docs/CONTROL_LOGIC_AUDIT.md)

**현재 컴퓨터에 하드웨어가 없으므로** 테스트 범위는 문법·단위 테스트·시뮬레이션이며, 실제 2023년 하드웨어 시험을 재현한 것은 아닙니다.
