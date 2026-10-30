import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'raspberry_pi'))
from line_tracer.protocol import SensorPacket, parse_packet, encode_result


class ProtocolTests(unittest.TestCase):
    def test_round_trip_request(self):
        self.assertEqual(parse_packet(b'5:2:3:0\r\n'), SensorPacket(5, 2, 3, 0))

    def test_reply(self):
        self.assertEqual(encode_result(0), b'0\n')
        self.assertEqual(encode_result(1), b'1\n')

    def test_bad_packet(self):
        for val in ('1:2:3', '1:2:3:2', '-1:2:3:0', 'a:b:c:d', ''):
            with self.subTest(val=val):
                with self.assertRaises(ValueError):
                    parse_packet(val)

    def test_bad_reply(self):
        with self.assertRaises(ValueError):
            encode_result(2)


if __name__ == '__main__':
    unittest.main()
