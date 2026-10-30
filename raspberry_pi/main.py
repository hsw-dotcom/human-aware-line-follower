"""2023년 사용자 설명에 맞춘 Pi 사람 검출 전담 복원본.

실제 2023년 최종 main.py 원문은 아직 확보되지 않았습니다.
Pi는 주행 중 반복적으로 카메라에서 프레임을 추출해 사람을 검출하고
사람 수를 '존재 여부 0/1'로만 변환해 Arduino로 전송합니다.
정지구간 색상·모터·재출발 버튼은 Arduino가 처리합니다.

신호 극성(현재 복원에서 선택, 최종 과거 파일 미확인):
    0 = 사람 없음
    1 = 사람 있음
11월 24일 '결과가 달라질 때만 송신' 사용자 요구를 적용하고,
최초 검출 결과는 반드시 한 번 전송합니다.
"""
from pathlib import Path

import count_objects

IMAGE_PATH = Path('/home/pi/project/image/before.jpg')  # Safe Watch 검출기 경로와 일치시킨 복원 선택
SERIAL_PORT = '/dev/ttyACM0'                              # 독립 시리얼 시험에서 확인
BAUD_RATE = 9600                                          # 사용자 제공 스케치에서 확인


def get_ip(interface='wlan0'):
    """2023년 사용자 코드에서 확인된 netifaces/wlan0 IP 조회."""
    import netifaces as ni
    info = ni.ifaddresses(interface)
    return info[ni.AF_INET][0]['addr']


def get_frame(ip, image_path=IMAGE_PATH):
    """기록에 등장한 MJPEG URL에서 프레임 한 장을 before.jpg에 저장."""
    import cv2

    url = 'http://' + ip + ':8000/stream.mjpg'
    capture = cv2.VideoCapture(url)
    try:
        ok, frame = capture.read()
    finally:
        capture.release()
    if not ok or frame is None:
        raise RuntimeError('MJPEG stream frame not available: ' + url)

    image_path.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(image_path), frame):
        raise OSError('image save failed: %s' % image_path)


def sample_people(ip):
    """정지구간 진입 여부와 관계없이 프레임을 추출하고 사람 수를 구함."""
    get_frame(ip)
    return count_objects.detect()


def people_to_flag(people_num):
    """Arduino에는 인원 수가 아니라 0/1 존재 여부만 전송."""
    return 1 if people_num != 0 else 0


def send_if_changed(ser, flag, previous_flag):
    """2023-11-24 변경 시 전송 요구의 복원; 첫 반복은 항상 전송."""
    if flag != previous_flag:
        ser.write((str(flag) + '\n').encode('ascii'))
    return flag


def run():
    """반복 촬영·인식 → Pi에서 0/1 변환 → Arduino로 존재 신호 송신."""
    import serial

    ip = get_ip()
    previous_flag = None
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as arduino:
        while True:
            people_num = sample_people(ip)
            flag = people_to_flag(people_num)
            previous_flag = send_if_changed(arduino, flag, previous_flag)


if __name__ == '__main__':
    run()
