"""하드웨어 없이 실행 가능한 핵심 판단 테스트."""
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "raspberry_pi"))
import main
from count_objects import count_people


class CoreTests(unittest.TestCase):
    def test_people_presence(self):
        self.assertEqual(main.people_to_flag(0), 0)
        self.assertEqual(main.people_to_flag(1), 1)
        self.assertEqual(main.people_to_flag(4), 1)

    def test_only_flag_is_transmitted(self):
        port = Mock()
        previous = None
        for count in (0, 0, 2, 3, 0):
            previous = main.send_if_changed(port, main.people_to_flag(count), previous)
        self.assertEqual(
            [call.args[0] for call in port.write.call_args_list],
            [b"0\n", b"1\n", b"0\n"],
        )

    def test_person_detection_class_and_confidence(self):
        self.assertEqual(count_people([0, 1, 0, 0], [0.6, 0.8, 0.1, 0.3]), 2)

    def test_update_interval(self):
        self.assertEqual(main.DETECTION_INTERVAL, 0.3)


if __name__ == "__main__":
    unittest.main()
