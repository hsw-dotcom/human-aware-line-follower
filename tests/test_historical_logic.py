"""카메라·Arduino 없이 대화 기반 주요 기능과 최신 요구사항 검증."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'raspberry_pi'))
import main


class HistoricalLogicTests(unittest.TestCase):
    def test_serial_format(self):
        self.assertEqual(main.parse_arduino_message('2:3:4:1\n'), (2, 3, 4, 1))
        self.assertEqual(main.parse_arduino_message(b'2:3:4:0\r\n'), (2, 3, 4, 0))
        for malformed in ('2:3:4', '2:3:4:7', 'wrong', '1:2:3:4:5'):
            with self.subTest(malformed=malformed), self.assertRaises(ValueError):
                main.parse_arduino_message(malformed)

    def test_recorded_rgb_expression(self):
        self.assertFalse(main.color_condition(1, 3, 3))
        self.assertTrue(main.color_condition(4, 3, 3))
        self.assertTrue(main.color_condition(3, 1, 3))
        self.assertTrue(main.color_condition(3, 3, 1))
        self.assertTrue(main.color_condition(0, 0, 0))  # 역사적 식의 한계

    def test_button_priority(self):
        self.assertEqual(main.decide_result(5, 1, 1, 1, 8, 0), 1)

    def test_zone_and_waiting_person_required(self):
        self.assertEqual(main.decide_result(5, 1, 1, 0, 0, 1), 1)
        self.assertEqual(main.decide_result(1, 3, 3, 0, 2, 1), 1)
        self.assertEqual(main.decide_result(5, 1, 1, 0, 1, 1), 0)

    def test_last_people_detection_already_exists_before_marker(self):
        state = main.LineTracerState()
        # 사람은 먼 곳에서 발견됐지만 아직 정지 구간이 아니므로 계속 주행.
        self.assertEqual(state.process(1, 3, 3, 0, 1, 0.0), 1)
        # 구간 감지 시점의 최신 검출값을 사용해 즉시 정지.
        self.assertEqual(state.process(5, 1, 1, 0, 1, 1.0), 0)

    def test_people_missing_at_marker_does_not_stop(self):
        state = main.LineTracerState()
        self.assertEqual(state.process(5, 1, 1, 0, 0, 1.0), 1)

    def test_stop_latch(self):
        state = main.LineTracerState()
        self.assertEqual(state.process(5, 1, 1, 0, 1, 1), 0)
        self.assertEqual(state.process(1, 3, 3, 0, 0, 2), 0)
        self.assertEqual(state.process(5, 1, 1, 0, 0, 3), 0)

    def test_button_restart_and_temporary_marker_ignore(self):
        state = main.LineTracerState(ignore_seconds=2)
        self.assertEqual(state.process(5, 1, 1, 0, 1, 1), 0)
        self.assertEqual(state.process(5, 1, 1, 1, 1, 2), 1)
        self.assertEqual(state.process(5, 1, 1, 0, 1, 3), 1)
        self.assertEqual(state.process(5, 1, 1, 0, 1, 4.1), 0)

    def test_button_hold_does_not_extend_ignore_time(self):
        state = main.LineTracerState(ignore_seconds=2)
        state.process(5, 1, 1, 1, 1, 1)
        state.process(5, 1, 1, 1, 1, 2)
        self.assertEqual(state.process(5, 1, 1, 0, 1, 3.1), 0)

    def test_ignore_range(self):
        for seconds in (0.5, 3.1):
            with self.subTest(seconds=seconds), self.assertRaises(ValueError):
                main.LineTracerState(ignore_seconds=seconds)


if __name__ == '__main__':
    unittest.main()
