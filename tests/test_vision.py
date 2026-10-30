import sys
import unittest
from concurrent.futures import Future
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'raspberry_pi'))
from line_tracer.vision import VisionWorker
from line_tracer.detector_adapter import people_count


class ManualExecutor:
    def __init__(self):
        self.jobs = []

    def submit(self, function):
        future = Future()
        self.jobs.append((future, function))
        return future

    def complete(self, index, error=None):
        future, function = self.jobs[index]
        if error is not None:
            future.set_exception(error)
        else:
            future.set_result(function())


class VisionTests(unittest.TestCase):
    def test_detector_return_shape_int(self):
        self.assertEqual(people_count(2), 2)
        self.assertEqual(people_count((3, ['obstacle'])), 3)

    def test_detector_rejects_unknown(self):
        for value in (-1, 0.0, True, None, [], ('a', None), (1,2,3)):
            with self.subTest(value=value), self.assertRaises(ValueError):
                people_count(value)

    def test_worker_only_one_inflight(self):
        executor = ManualExecutor()
        worker = VisionWorker(lambda: 2, executor=executor, interval_seconds=0.5)
        self.assertTrue(worker.request(1.0))
        self.assertFalse(worker.request(1.1))
        executor.complete(0)
        worker.poll()
        self.assertEqual(worker.last_people, 2)
        self.assertTrue(worker.valid)
        self.assertFalse(worker.request(1.2))
        self.assertTrue(worker.request(1.5))

    def test_worker_discards_old_result_after_restart(self):
        executor = ManualExecutor()
        worker = VisionWorker(lambda: 4, executor=executor, interval_seconds=0)
        worker.request(1.0)
        worker.invalidate()
        executor.complete(0)
        worker.poll()
        self.assertFalse(worker.valid)
        self.assertEqual(worker.last_people, 0)
        self.assertTrue(worker.request(1.1))
        executor.complete(1)
        worker.poll()
        self.assertTrue(worker.valid)
        self.assertEqual(worker.last_people, 4)

    def test_worker_failure_latches(self):
        executor = ManualExecutor()
        worker = VisionWorker(lambda: 0, executor=executor, interval_seconds=0)
        worker.request(0)
        executor.complete(0, RuntimeError('camera disconnected'))
        worker.poll()
        self.assertTrue(worker.failed)
        self.assertIn('camera disconnected', worker.last_error)


if __name__ == '__main__':
    unittest.main()
