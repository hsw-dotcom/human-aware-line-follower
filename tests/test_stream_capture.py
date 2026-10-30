"""과거 사용자 get_ip/get_frame 함수의 입력·출력 경로를 오프라인 검증."""
import sys
import tempfile
import unittest
from pathlib import Path
from types import ModuleType
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'raspberry_pi'))
import main


class StreamFrameTests(unittest.TestCase):
    def test_get_ip_uses_wlan0(self):
        ni = ModuleType('netifaces')
        ni.AF_INET = 2
        addresses = []
        def ifaddresses(interface):
            addresses.append(interface)
            return {2: [{'addr': '192.0.2.10'}]}
        ni.ifaddresses = ifaddresses
        with patch.dict(sys.modules, {'netifaces': ni}):
            self.assertEqual(main.get_ip(), '192.0.2.10')
        self.assertEqual(addresses, ['wlan0'])

    def test_get_frame_uses_historical_mjpeg_url(self):
        cv = ModuleType('cv2')
        opened = []
        written = []
        class FakeCapture:
            def __init__(self, url):
                opened.append(url)
                self.released = False
            def read(self):
                return True, 'frame-data'
            def release(self):
                self.released = True
        cv.VideoCapture = FakeCapture
        def imwrite(path, image):
            written.append((path, image))
            return True
        cv.imwrite = imwrite
        with tempfile.TemporaryDirectory() as tmp, patch.dict(sys.modules, {'cv2': cv}):
            path = Path(tmp) / 'image' / 'before.jpg'
            main.get_frame('192.0.2.10', path)
            self.assertTrue(path.parent.exists())
            self.assertEqual(written, [(str(path), 'frame-data')])
        self.assertEqual(opened, ['http://192.0.2.10:8000/stream.mjpg'])

    def test_get_frame_fails_on_empty_read(self):
        cv = ModuleType('cv2')
        class EmptyCapture:
            def __init__(self, url):
                pass
            def read(self):
                return False, None
            def release(self):
                pass
        cv.VideoCapture = EmptyCapture
        cv.imwrite = lambda path, image: True
        with tempfile.TemporaryDirectory() as tmp, patch.dict(sys.modules, {'cv2': cv}):
            with self.assertRaises(RuntimeError):
                main.get_frame('192.0.2.10', Path(tmp) / 'before.jpg')

    def test_sample_people_calls_frame_before_detect(self):
        order = []
        with patch.object(main, 'get_frame', side_effect=lambda ip: order.append(('frame', ip))):
            with patch.object(main.count_objects, 'detect', side_effect=lambda: order.append(('detect',)) or 2):
                self.assertEqual(main.sample_people('192.0.2.10'), 2)
        self.assertEqual(order, [('frame', '192.0.2.10'), ('detect',)])


if __name__ == '__main__':
    unittest.main()
