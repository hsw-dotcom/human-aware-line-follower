"""Pi 0.3초 사람 존재 갱신과 Arduino의 색상·사람 동시 정지 조건 모의.

Arduino 코드 자체를 실행한 테스트는 아니며, 역할·상태 전이 검토 예시입니다.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'raspberry_pi'))
from main import people_to_flag, UPDATE_INTERVAL_SECONDS

def arduino_decision(stopped, stop_zone, person_flag, button_pressed, ignoring):
    """사용자 확인 동작을 모델링. 실제 Arduino 동작 검증은 아님."""
    if button_pressed:
        return False
    if ignoring:
        return stopped
    return stopped or (stop_zone and person_flag == 1)

def exercise():
    assert UPDATE_INTERVAL_SECONDS == 0.3
    stopped = False
    cases = [
        ('먼 시야에 사람 있지만 일반 구간', False, 3, False, False, False),
        ('구간에 사람 없음', True, 0, False, False, False),
        ('구간에서 사람 확인 후 정지', True, 1, False, False, True),
        ('사람 사라져도 정지 유지', False, 0, False, False, True),
        ('적재 후 버튼 입력', True, 1, True, False, False),
        ('무시 중 색·사람 모두 있어도 통과', True, 1, False, True, False),
        ('무시 만료 뒤 두 조건 다시 충족', True, 1, False, False, True),
    ]
    for label, zone, people_count, button, ignoring, expected in cases:
        flag = people_to_flag(people_count)  # Pi: 0.3초마다 갱신되는 사람 존재 여부
        stopped = arduino_decision(stopped, zone, flag, button, ignoring)
        assert stopped == expected, label
        print(f'{label}: Pi flag={flag}, Arduino stop-zone={zone} -> {"STOP" if stopped else "RUN"}')

if __name__ == '__main__':
    exercise()
