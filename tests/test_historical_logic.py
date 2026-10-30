"""Pi의 인원 수→0/1 변환 및 변경 시 전송 검증. Arduino와 RGB 판단은 Pi의 책임이 아님."""
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'raspberry_pi'))
import main


class PiRoleTests(unittest.TestCase):
    def test_update_interval_is_300ms(self):
        self.assertEqual(main.UPDATE_INTERVAL_SECONDS, 0.3)

    def test_wait_until_next_sample(self):
        calls = []
        main.wait_until(1.3, lambda: 1.0, calls.append)
        self.assertAlmostEqual(calls[0], 0.3)
        main.wait_until(1.3, lambda: 1.5, calls.append)
        self.assertEqual(len(calls), 1)

    def test_arduino_color_processing_is_not_done_in_pi(self):
        self.assertFalse(hasattr(main, 'isStopZone'))
        self.assertFalse(hasattr(main, 'IGNORE_MS'))

    def test_zero_people_is_zero(self):
        self.assertEqual(main.people_to_flag(0), 0)

    def test_one_or_multiple_people_is_one(self):
        self.assertEqual(main.people_to_flag(1), 1)
        self.assertEqual(main.people_to_flag(3), 1)
        self.assertEqual(main.people_to_flag(10), 1)

    def test_first_zero_is_sent(self):
        ser = Mock()
        prev = main.send_if_changed(ser, 0, None)
        self.assertEqual(prev, 0)
        ser.write.assert_called_once_with(b'0\n')

    def test_send_only_on_change(self):
        ser = Mock()
        prev = None
        for count in [0, 0, 2, 5, 0, 0]:
            prev = main.send_if_changed(ser, main.people_to_flag(count), prev)
        self.assertEqual([c.args[0] for c in ser.write.call_args_list],
                         [b'0\n', b'1\n', b'0\n'])

    def test_pi_does_not_include_color_or_button_logic(self):
        self.assertFalse(hasattr(main, 'color_condition'))
        self.assertFalse(hasattr(main, 'LineTracerState'))
        self.assertFalse(hasattr(main, 'parse_arduino_message'))

    def test_only_presence_not_raw_count_is_sent(self):
        ser = Mock()
        main.send_if_changed(ser, main.people_to_flag(8), None)
        ser.write.assert_called_once_with(b'1\n')


if __name__ == '__main__':
    unittest.main()
