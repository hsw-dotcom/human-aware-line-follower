"""Arduino가 정지구간과 Pi의 0/1 사람 존재 플래그를 결합하는 개념 모의.

실제 Arduino 하드웨어/스케치 실행 테스트가 아닌 Python 상태 전이 예시입니다.
Pi는 '사람이 있는지 0/1'만 판단하며 색상은 알지 못합니다.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'raspberry_pi'))
from main import people_to_flag

stopped = False
restart_ignore_until = -1.0
examples = [
    ('일반 구간 · 사람 없음', False, 0, False, 0.0),
    ('먼 시야 사람 인식 · 구간 전', False, 2, False, 1.0),
    ('정지구간 도착 · 사람 없음', True, 0, False, 2.0),
    ('정지구간 도착 · 사람 있음', True, 1, False, 3.0),
    ('사람 사라짐 · 정지 유지', False, 0, False, 4.0),
    ('적재 후 버튼 재출발', True, 1, True, 5.0),
    ('무시 시간 중 통과', True, 1, False, 6.0),
    ('무시 종료 후 구간 재감지', True, 1, False, 7.1),
]
for title, stop_zone, people_count, button, now in examples:
    flag = people_to_flag(people_count)   # Pi 작업
    if button:
        stopped = False
        restart_ignore_until = now + 2.0  # 1~3초 중 예시값
    elif now >= restart_ignore_until and stop_zone and flag == 1:
        stopped = True                  # Arduino 작업
    print(f'{title}: Pi={flag} Arduino-zone={stop_zone} → {"STOP" if stopped else "RUN"}')
