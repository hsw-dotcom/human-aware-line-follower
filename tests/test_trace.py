import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'raspberry_pi'))
from line_tracer.protocol import SensorPacket, parse_packet, encode_result
from line_tracer.decision import decide_result, Controller


class TraceTests(unittest.TestCase):
    def test_historical_truth_table(self):
        cases = [
            # button, red, people, previous, expected
            (1, False, 0, 0, 1),
            (1, True, 5, 0, 1),
            (0, True, 0, 1, 0),
            (0, False, 2, 1, 0),
            (0, False, 0, 0, 0),
            (0, False, 0, 1, 1),
        ]
        for button, red, people, previous, expected in cases:
            rgb = (5, 1, 1) if red else (2, 3, 3)
            packet = SensorPacket(*rgb, button)
            with self.subTest(button=button, red=red, people=people, previous=previous):
                self.assertEqual(decide_result(packet, people, previous), expected)

    def test_button_held_does_not_prolong_ignore(self):
        c = Controller(restart_ignore_seconds=3)
        c.update(SensorPacket(5, 1, 1, 1), 1, 10)
        c.update(SensorPacket(5, 1, 1, 1), 1, 12)
        self.assertEqual(c.ignore_until, 13)

    def test_protocol_wire_format(self):
        self.assertEqual(parse_packet('4:2:0:1\r\n'), SensorPacket(4, 2, 0, 1))
        self.assertEqual(encode_result(0), b'0\n')
        self.assertEqual(encode_result(1), b'1\n')


if __name__ == '__main__':
    unittest.main()
