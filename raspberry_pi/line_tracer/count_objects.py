"""Compatibility name from historical notes.

This is NOT the original count_objects.py or the original trained model.
The example OpenCV HOG person detector may miss people, especially on a Pi
and at the 3-5 meter range in the demonstration. Replace with original model
when recovered.
"""
from pathlib import Path


def detect(image_path: str | Path = 'runtime/before.jpg') -> int:
    """Count bounding boxes returned by OpenCV's stock HOG pedestrian detector."""
    import cv2
    image = cv2.imread(str(image_path))
    if image is None:
        raise FileNotFoundError(f'cannot load image: {image_path}')
    detector = cv2.HOGDescriptor()
    detector.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    boxes, _weights = detector.detectMultiScale(
        image, winStride=(8, 8), padding=(8, 8), scale=1.05)
    return len(boxes)
