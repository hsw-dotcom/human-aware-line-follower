"""실물 기기 없이 기록된 상태 전이 확인. 임의의 RGB·검출 결과는 예시값."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'raspberry_pi'))
import main

state = main.LineTracerState(ignore_seconds=2.0)
scenarios = [
    ('일반 바닥/주행', (1, 3, 3, 0), 0.0, 0),
    ('색 구간/대기자 없음: 통과', (5, 1, 1, 0), 0.5, 0),
    ('색 구간/대기자 있음: 정지', (5, 1, 1, 0), 1.0, 1),
    ('색 구간 이탈/정지 유지', (1, 3, 3, 0), 1.5, 0),
    ('재출발 버튼', (5, 1, 1, 1), 2.0, 0),
    ('재출발 직후 무시', (5, 1, 1, 0), 3.0, 1),
    ('무시시간 종료 뒤 정지', (5, 1, 1, 0), 4.1, 1),
]
for label, (r,g,b,button), now, people in scenarios:
    result = state.process(r,g,b,button,lambda: people,now)
    print(f'{label:21} RGB=({r},{g},{b}) button={button} people={people} → result={result}')
