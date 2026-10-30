"""정지구간 도달 이전에 사람을 이미 발견한 상황을 모의."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'raspberry_pi'))
import main

state = main.LineTracerState(ignore_seconds=2.0)
scenarios = [
    ('사람 없음 / 일반 구간', (1, 3, 3, 0), 0.0, 0),
    ('먼 시야 사람 검출 / 구간 전', (1, 3, 3, 0), 1.0, 1),
    ('정지구간 도착 / 사람 인식 유지', (5, 1, 1, 0), 2.0, 1),
    ('사람 사라짐 / 정지 유지', (1, 3, 3, 0), 3.0, 0),
    ('적재 완료 / 버튼 재출발', (5, 1, 1, 1), 4.0, 0),
    ('재출발 직후 정지구간 무시', (5, 1, 1, 0), 5.0, 1),
    ('무시시간 후 정지구간 / 사람 있음', (5, 1, 1, 0), 6.1, 1),
]
for label, (r, g, b, button), now, people_num in scenarios:
    result = state.process(r, g, b, button, people_num, now)
    print(f'{label:26} RGB=({r},{g},{b}) button={button} people={people_num} → result={result}')
