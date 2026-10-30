"""Unittest: no camera, serial, or Arduino is needed."""
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'raspberry_pi'))
from line_tracer.decision import Controller, decide_result
from line_tracer.protocol import SensorPacket


class DecisionTests(unittest.TestCase):
    def test_color_rule(self):
        self.assertTrue(SensorPacket(4, 3, 3, 0).color_condition)
        self.assertTrue(SensorPacket(3, 1, 3, 0).color_condition)
        self.assertFalse(SensorPacket(3, 3, 3, 0).color_condition)

    def test_button_overrides_color_and_people(self):
        self.assertEqual(decide_result(SensorPacket(8, 1, 1, 1), 2, 0), 1)

    def test_color_stops(self):
        self.assertEqual(decide_result(SensorPacket(5, 2, 2, 0), 0, 1), 0)

    def test_people_stop_even_without_color(self):
        self.assertEqual(decide_result(SensorPacket(3, 3, 3, 0), 1, 1), 0)

    def test_previous_state_kept(self):
        self.assertEqual(decide_result(SensorPacket(3, 3, 3, 0), 0, 0), 0)
        self.assertEqual(decide_result(SensorPacket(3, 3, 3, 0), 0, 1), 1)

    def test_ignore_after_button(self):
        c = Controller(restart_ignore_seconds=2.0)
        self.assertEqual(c.update(SensorPacket(5, 2, 2, 0), 0, 10.0), 0)
        self.assertEqual(c.update(SensorPacket(5, 2, 2, 1), 0, 11.0), 1)
        self.assertFalse(c.should_detect(SensorPacket(5, 2, 2, 0), 12.0))
        self.assertEqual(c.update(SensorPacket(5, 2, 2, 0), 99, 12.0), 1)
        self.assertEqual(c.update(SensorPacket(5, 2, 2, 0), 0, 13.1), 0)

    def test_held_button_does_not_extend_timeout_forever(self):
        c = Controller(restart_ignore_seconds=2.0)
        c.update(SensorPacket(3, 3, 3, 1), 0, 1.0)
        c.update(SensorPacket(3, 3, 3, 1), 0, 4.0)
        self.assertEqual(c.ignore_until, 3.0)


if __name__ == '__main__':
    unittest.main()
