import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'raspberry_pi'))
import main

class HistoricalLogicTests(unittest.TestCase):
    def test_serial_format(self):
        self.assertEqual(main.parse_arduino_message('2:3:4:1\n'), (2,3,4,1))
        self.assertEqual(main.parse_arduino_message(b'2:3:4:0\r\n'), (2,3,4,0))
        for malformed in ('2:3:4','2:3:4:7','wrong','1:2:3:4:5'):
            with self.subTest(malformed=malformed), self.assertRaises(ValueError):
                main.parse_arduino_message(malformed)

    def test_recorded_rgb_expression(self):
        self.assertFalse(main.color_condition(1,3,3))
        self.assertTrue(main.color_condition(4,3,3))
        self.assertTrue(main.color_condition(3,1,3))
        self.assertTrue(main.color_condition(3,3,1))
        self.assertTrue(main.color_condition(0,0,0))

    def test_button_priority(self):
        self.assertEqual(main.decide_result(5,1,1,1,8,0), 1)

    def test_stop_requires_zone_and_person(self):
        self.assertEqual(main.decide_result(5,1,1,0,0,1), 1)
        self.assertEqual(main.decide_result(1,3,3,0,2,1), 1)
        self.assertEqual(main.decide_result(5,1,1,0,1,1), 0)
        self.assertEqual(main.decide_result(5,1,1,0,2,1), 0)

    def test_stop_latches_even_after_person_leaves(self):
        self.assertEqual(main.decide_result(5,1,1,0,0,0), 0)
        self.assertEqual(main.decide_result(1,3,3,0,0,0), 0)

    def test_same_marker_with_zero_or_one_person_changes_output(self):
        state = main.LineTracerState()
        self.assertEqual(state.process(5,1,1,0,lambda: 0,1),1)
        self.assertEqual(state.process(5,1,1,0,lambda: 1,2),0)
        self.assertEqual(state.process(5,1,1,0,lambda: 0,3),0)

    def test_person_outside_marker_does_not_trigger_camera(self):
        state = main.LineTracerState()
        called=[]
        self.assertEqual(state.process(1,3,3,0,lambda: called.append(1) or 4,1),1)
        self.assertEqual(called,[])


    def test_previous_state_retained(self):
        self.assertEqual(main.decide_result(1,3,3,0,0,0), 0)
        self.assertEqual(main.decide_result(1,3,3,0,0,1), 1)

    def test_camera_only_triggered_in_marker_zone(self):
        state=main.LineTracerState()
        called=[]
        result=state.process(1,3,3,0,lambda: called.append('shot') or 1,0)
        self.assertEqual(result,1)
        self.assertEqual(called,[])
        result=state.process(5,1,1,0,lambda: called.append('shot') or 0,1)
        self.assertEqual(result,1)  # 사람 0명은 정지하지 않음
        self.assertEqual(called,['shot'])

    def test_button_restarts_for_two_seconds(self):
        state=main.LineTracerState(ignore_seconds=2)
        state.process(5,1,1,0,lambda: 1,1)
        self.assertEqual(state.process(5,1,1,1,lambda: 1,2),1)
        self.assertEqual(state.process(5,1,1,0,lambda: 1,3),1)
        self.assertEqual(state.process(5,1,1,0,lambda: 1,4.1),0)

    def test_no_repeated_camera_when_ignore_active(self):
        state=main.LineTracerState(ignore_seconds=2)
        state.process(5,1,1,1,lambda: 0,1)
        called=[]
        state.process(5,1,1,0,lambda: called.append(1) or 0,2)
        self.assertEqual(called,[])

    def test_held_button_does_not_extend_timer(self):
        state=main.LineTracerState(ignore_seconds=2)
        state.process(5,1,1,1,lambda: 0,1)
        state.process(5,1,1,1,lambda: 0,2)
        self.assertEqual(state.process(5,1,1,0,lambda: 1,3.1),0)

    def test_ignore_time_documented_range(self):
        for seconds in (0.5,3.1):
            with self.subTest(seconds=seconds),self.assertRaises(ValueError):
                main.LineTracerState(ignore_seconds=seconds)

if __name__=='__main__': unittest.main()
