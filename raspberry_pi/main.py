"""2023년 당시 대화에 충실하게 복원한 Raspberry Pi 측 단일 루프.

실제 2023년 소스 전문은 확인되지 않았음.
확정: r:g:b:button -> result(0/1); before.jpg -> count_objects.detect();
       실제 목표: 특정 구간에서 대기 중인 사람이 있을 때만 정지;
       과거 대화의 색 OR 사람 조건은 docs/CONTROL_LOGIC_AUDIT.md에 원문 보존;
       버튼 재시작 뒤 1~3초 감지 무시.
추정: 시리얼 포트/속도, 카메라 세부 초기화, 반복 호출 위치, 줄바꿈 종결.
"""
import time
from pathlib import Path

import count_objects

# 아래 항목은 Safe Watch 원본의 저장 경로를 참고한 임시값입니다.
# 라인트레이서에서 똑같은 경로를 썼다는 원본 증거는 없습니다.
IMAGE_PATH = Path('/home/pi/project/image/before.jpg')
SERIAL_PORT = '/dev/ttyACM0'      # 미확인
BAUD_RATE = 9600                  # 미확인
RESTART_IGNORE_SECONDS = 2.0      # 대화에서 시험한 1~3초 범위의 예시값, 최종 확정 아님


def parse_arduino_message(line):
    """Arduino가 보낸 r:g:b:button 4개 정수 파싱."""
    if isinstance(line, bytes):
        line = line.decode('ascii').strip()
    parts = line.strip().split(':')
    if len(parts) != 4:
        raise ValueError('expected r:g:b:button')
    r, g, b, button = [int(x) for x in parts]
    if button not in (0, 1):
        raise ValueError('button must be 0 or 1')
    return r, g, b, button


def color_condition(r, g, b):
    """대화에서 확정한 색상 판단식. 논리적 예외도 임의 변경하지 않음."""
    return r >= 4 or r >= 2 * g or r >= 2 * b


def decide_result(r, g, b, button, people_num, previous_result):
    """2026년 목표 교정 복원: 버튼 > (작업 구간 AND 대기자) > 이전 상태.

    과거 대화에 남은 OR 조건식은 문서에 원형 그대로 보존.
    이 AND 변경은 역사적 원문 재현이 아닌 사용자 목표를 반영한 수정.
    """
    if button == 1:
        return 1
    if color_condition(r, g, b) and people_num != 0:
        return 0
    return previous_result


class LineTracerState:
    """정지 상태 기억과 재출발 직후 감지 무시를 최소한으로 구현."""
    def __init__(self, ignore_seconds=RESTART_IGNORE_SECONDS):
        if not 1.0 <= ignore_seconds <= 3.0:
            raise ValueError('2023년 대화 기록의 무시 시간 범위는 1~3초')
        self.previous_result = 1
        self.ignore_seconds = ignore_seconds
        self.ignore_until = 0.0
        self.button_was_pressed = False

    def process(self, r, g, b, button, detect_people, now):
        """detect_people()는 필요한 시점에 `before.jpg` 촬영 후 검출한 수를 반환.

        재시작 버튼의 연속 눌림 중 무시 시간을 계속 연장하지 않도록 구성한 것은
        원문에서 직접 확인된 줄은 아니고, '일정 시간 감지 무시' 동작의 최소 해석.
        """
        if button == 1:
            if not self.button_was_pressed:
                self.ignore_until = now + self.ignore_seconds
            self.button_was_pressed = True
            self.previous_result = 1
            return 1

        self.button_was_pressed = False
        if now < self.ignore_until:
            self.previous_result = 1
            return 1

        people_num = 0
        # 색상은 '사람을 검사할 구간' 표시일 뿐 단독 정지 조건이 아님.
        # 촬영 구간·시간 및 대기자 ROI는 원본 미확보로 추정.
        if color_condition(r, g, b):
            people_num = detect_people()
        self.previous_result = decide_result(
            r, g, b, button, people_num, self.previous_result)
        return self.previous_result


def take_picture(picam2, image_path=IMAGE_PATH):
    """카메라 1프레임 촬영 후 before.jpg 저장 (색 형식은 환경별 확인 필요)."""
    import cv2
    frame = picam2.capture_array()
    image_path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(image_path), frame):
        raise OSError('image save failed: %s' % image_path)


def run():
    """동기식 읽기→촬영→검출→회신. 후대의 비동기 워커 사용 안 함."""
    import serial
    from picamera2 import Picamera2

    state = LineTracerState()
    picam2 = Picamera2()
    # 해상도와 이미지 포맷은 기록 부재로 구체 값을 확정하지 않았음.
    picam2.configure(picam2.create_preview_configuration())
    picam2.start()
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as arduino:
            while True:
                line = arduino.readline()
                if not line:
                    continue
                try:
                    r, g, b, button = parse_arduino_message(line)
                except (ValueError, UnicodeDecodeError):
                    # 원본 오류 처리 방식 미확인. 잘못된 요청은 이번 주기에 무시.
                    continue

                def detect_people():
                    take_picture(picam2, IMAGE_PATH)
                    # 당시 대화의 호출 이름을 보존: count_objects.detect()
                    return count_objects.detect()

                result = state.process(
                    r, g, b, button, detect_people, time.monotonic())
                # 당시 Pi->Arduino 결과는 0 또는 1로 확인.
                # 줄바꿈을 사용했는지는 확인되지 않음.
                arduino.write((str(result) + '\n').encode('ascii'))
    finally:
        picam2.stop()


if __name__ == '__main__':
    run()
