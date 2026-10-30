"""Raspberry Pi 사람 인식·0/1 전송 복원 예시 (2023년 최종 원본 아님)."""
import time
from pathlib import Path
import count_objects

BASE_DIR = Path(__file__).resolve().parent
IMAGE_PATH = BASE_DIR / "image" / "before.jpg"
SERIAL_PORT = "/dev/ttyACM0"
BAUD_RATE = 9600
DETECTION_INTERVAL = 0.3


def get_ip(interface="wlan0"):
    import netifaces
    return netifaces.ifaddresses(interface)[netifaces.AF_INET][0]["addr"]


def get_frame(ip):
    """MJPEG 스트림에서 한 프레임을 저장합니다."""
    import cv2
    stream = cv2.VideoCapture(f"http://{ip}:8000/stream.mjpg")
    try:
        ok, frame = stream.read()
    finally:
        stream.release()
    if not ok or frame is None:
        raise RuntimeError("카메라 프레임을 읽지 못했습니다.")
    IMAGE_PATH.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(IMAGE_PATH), frame):
        raise OSError("이미지 저장 실패")


def people_to_flag(people_count):
    return 1 if people_count > 0 else 0


def send_if_changed(serial_port, current, previous):
    """최초 1회와 변경 시 송신하는 복원 선택."""
    if current != previous:
        serial_port.write(f"{current}\n".encode("ascii"))
    return current


def main():
    import serial
    ip = get_ip()
    previous = None
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1) as port:
        while True:
            started = time.monotonic()
            get_frame(ip)
            people_count = count_objects.detect()
            previous = send_if_changed(port, people_to_flag(people_count), previous)
            time.sleep(max(0, DETECTION_INTERVAL - (time.monotonic() - started)))


if __name__ == "__main__":
    main()
