"""2023년 11월 23~24일 대화의 실행 순서에 근거한 Pi 제어 복원본.

실제 2023년 최종 파일은 확보되지 않았음.
대화 속 사용자의 main.py: 반복 get_frame(ip) -> count_objects.detect()
-> Arduino 송수신; 색상 구간에서만 촬영하는 분기 없음.
사용자 확인: 먼 시야에서 미리 사람을 인식하고, 정지 구간을
색상 센서가 감지할 때 사람 인식 결과를 함께 판정함.
이 파일의 camera/serial 설정, 결과값 연동은 복원 및 추정.
"""
import time
from pathlib import Path

import count_objects

# Safe Watch 원본을 참조한 예시 경로. 2023년 라인트레이서의 최종 경로 미확인.
IMAGE_PATH = Path('/home/pi/project/image/before.jpg')
SERIAL_PORT = '/dev/ttyACM0'     # 독립 시리얼 시험 원문에서 확인; 최종 통합 포트 미확인
BAUD_RATE = 9600                 # Arduino/시리얼 시험 코드에서 확인
RESTART_IGNORE_SECONDS = 2.0    # 당시 1~3초 시험, 실제 최종 고정값 미확인


def parse_arduino_message(line):
    """Arduino -> Pi 형식 한 버전: r:g:b:button."""
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
    """당시 대화에 남은 RGB 판정식. 0:0:0도 참인 문제를 고치지 않음."""
    return r >= 4 or r >= 2 * g or r >= 2 * b


def decide_result(r, g, b, button, people_num, previous_result):
    """현재 목적 반영: 정지구간 AND 사람 검출에서만 새로 정지.

    2023년 대화의 '색 OR 사람' 식은 docs/CONTROL_LOGIC_AUDIT.md에 보존.
    정확한 2023년 최종 조건식은 확인되지 않았음.
    """
    if button == 1:
        return 1
    if color_condition(r, g, b) and people_num != 0:
        return 0
    return previous_result


class LineTracerState:
    """정지 유지 및 버튼 재출발 후 구간 정지 조건 일시 무시(최종 시간 미확인)."""

    def __init__(self, ignore_seconds=RESTART_IGNORE_SECONDS):
        if not 1.0 <= ignore_seconds <= 3.0:
            raise ValueError('대화에서 시험한 범위는 1~3초')
        self.previous_result = 1   # 초기 상태는 복원 가정
        self.ignore_seconds = ignore_seconds
        self.ignore_until = 0.0
        self.button_was_pressed = False

    def process(self, r, g, b, button, people_num, now):
        """이미 수행된 영상 검출의 최신 사람 수와 현재 구간 센싱을 결합.

        이 함수는 촬영을 실행하지 않습니다. 2023년의 정확한 촬영 주기,
        과거 검출 결과 캐싱 여부 및 정지 지점까지의 이동 로직은 미확인.
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

        self.previous_result = decide_result(
            r, g, b, button, people_num, self.previous_result)
        return self.previous_result


def take_picture(picam2, image_path=IMAGE_PATH):
    """카메라에서 1프레임 받아 before.jpg 저장. 설정/색상 형식은 추정."""
    import cv2
    frame = picam2.capture_array()
    image_path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(image_path), frame):
        raise OSError('image save failed: %s' % image_path)


def sample_people(picam2):
    """정지구간 센싱 전에도 반복되는 1회 촬영 및 사람 수 검출."""
    take_picture(picam2, IMAGE_PATH)
    return count_objects.detect()


def run():
    """반복 프레임 추출→사람 인식→Arduino RGB/버튼 수신→판정→회신."""
    import serial
    from picamera2 import Picamera2

    state = LineTracerState()
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration())
    picam2.start()
    try:
        with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as arduino:
            while True:
                # 실제 11/23~24 대화의 Pi 루프에서는 촬영·검출이 먼저 실행됨.
                # 이 코드는 매회 새 이미지를 처리하며 별도의 사람 검출 캐시를 만들지 않음.
                people_num = sample_people(picam2)
                line = arduino.readline()
                if not line:
                    continue
                try:
                    r, g, b, button = parse_arduino_message(line)
                except (ValueError, UnicodeDecodeError):
                    continue
                result = state.process(
                    r, g, b, button, people_num, time.monotonic())
                # 개행/0,1 극성은 이 개발 단계에서 사용한 한 가지 통신 계약.
                arduino.write((str(result) + '\n').encode('ascii'))
    finally:
        picam2.stop()


if __name__ == '__main__':
    run()
