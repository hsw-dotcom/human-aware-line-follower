import sys
import unittest
from concurrent.futures import Future
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'raspberry_pi'))
from line_tracer.coordinator import Coordinator
from line_tracer.decision import Controller
from line_tracer.protocol import SensorPacket
from line_tracer.vision import VisionWorker


class ManualExecutor:
    def __init__(self): self.futures = []
    def submit(self, function):
        f = Future()
        self.futures.append(f)
        return f


class CoordinatorTests(unittest.TestCase):
    def setUp(self):
        self.executor = ManualExecutor()
        self.vision = VisionWorker(lambda: 1, executor=self.executor, interval_seconds=0.0)
        self.control = Coordinator(Controller(restart_ignore_seconds=2), self.vision)
        self.clear = SensorPacket(2, 3, 3, 0)
        self.zone = SensorPacket(5, 1, 1, 0)
        self.button = SensorPacket(5, 1, 1, 1)

    def test_ordinary_line_follow(self):
        self.assertEqual(self.control.process(self.clear, 0).result, 1)
        self.assertFalse(self.control.process(self.clear, 0).vision_pending)

    def test_marker_stops_immediately_without_waiting_for_camera(self):
        state = self.control.process(self.zone, 1)
        self.assertEqual(state.result, 0)
        self.assertTrue(state.vision_pending)
        self.assertTrue(state.detection_started)
        self.assertEqual(len(self.executor.futures), 1)

    def test_positive_person_response_preserves_stop_when_marker_passed(self):
        self.control.process(self.zone, 1)
        self.executor.futures[0].set_result(1)
        result = self.control.process(self.clear, 2)
        self.assertEqual(result.people, 1)
        self.assertEqual(result.result, 0)

    def test_button_and_ignore_prevent_stop(self):
        self.control.process(self.zone, 1)
        self.executor.futures[0].set_result(1)
        self.control.process(self.clear, 1.5)
        self.assertEqual(self.control.process(self.button, 2).result, 1)
        self.assertEqual(self.control.process(self.zone, 3).result, 1)
        self.assertEqual(self.control.process(self.zone, 4.2).result, 0)

    def test_restart_ignores_stale_inflight_result(self):
        self.control.process(self.zone, 1)
        self.control.process(self.button, 1.5)
        self.executor.futures[0].set_result(5)
        state = self.control.process(self.clear, 2)
        self.assertEqual(state.result, 1)
        self.assertEqual(state.people, 0)
        self.assertFalse(self.vision.valid)

    def test_camera_failure_stops(self):
        self.control.process(self.zone, 1)
        self.executor.futures[0].set_exception(RuntimeError('sensor failure'))
        state = self.control.process(self.clear, 2)
        self.assertTrue(state.vision_failed)
        self.assertEqual(state.result, 0)

    def test_dark_zero_rgb_documented_true(self):
        self.assertTrue(SensorPacket(0, 0, 0, 0).color_condition)

    def test_performance_avoid_constant_detection(self):
        for n in range(10):
            self.control.process(self.clear, n / 10)
        self.assertEqual(len(self.executor.futures), 0)

    def test_detect_always_stops_while_pending(self):
        control = Coordinator(Controller(), self.vision, detect_always=True)
        result = control.process(self.clear, 1)
        self.assertTrue(result.vision_pending)
        self.assertEqual(result.result, 0)


if __name__ == '__main__':
    unittest.main()
