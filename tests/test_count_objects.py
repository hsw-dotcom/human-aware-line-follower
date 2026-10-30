import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'raspberry_pi'))
from line_tracer.count_objects import (
    _count_people, _indices, DEFAULT_MODEL, MODEL_IMAGE_SIZE,
    MIN_CONFIDENCE, PERSON_CLASS_ID,
)


class PeopleDetectionExtractionTests(unittest.TestCase):
    def test_safe_watch_original_threshold_and_class_filter(self):
        classes = [0, 0, 1, 0, 2, 0]
        scores = [0.2, 0.1999, 0.99, 0.88, 1.0, 0.0]
        self.assertEqual(_count_people(classes, scores), 2)
        self.assertEqual(_count_people([0.9, 0.0], [0.9, 0.9]), 1)

    def test_no_detection(self):
        self.assertEqual(_count_people([], []), 0)
        self.assertEqual(_count_people([1, 2], [0.8, 0.9]), 0)

    def test_custom_threshold_is_explicit_reconstruction_option(self):
        self.assertEqual(_count_people([0, 0], [0.4, 0.8], threshold=0.5), 1)
        for bad in (-0.1, 1.1):
            with self.assertRaises(ValueError):
                _count_people([0], [0.5], threshold=bad)

    def test_inconsistent_output_lengths(self):
        with self.assertRaises(ValueError):
            _count_people([0, 0], [0.9])

    def test_safe_watch_output_head_index_rules(self):
        self.assertEqual(_indices([{'name': 'StatefulPartitionedCall:0'}]
                                  + [{'name': 'x'}]*3), (3, 0))
        self.assertEqual(_indices([{'name': 'TFLite_Detection_PostProcess'}]
                                  + [{'name': 'x'}]*3), (1, 2))
        with self.assertRaises(ValueError):
            _indices([{'name': 'x'}])

    def test_original_constants_preserved(self):
        self.assertEqual(MODEL_IMAGE_SIZE, (640, 640))
        self.assertEqual(MIN_CONFIDENCE, 0.2)
        self.assertEqual(PERSON_CLASS_ID, 0)
        self.assertEqual(DEFAULT_MODEL.name, 'people_detect.tflite')


if __name__ == '__main__':
    unittest.main()
