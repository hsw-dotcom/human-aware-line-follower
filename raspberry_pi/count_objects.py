"""Safe Watch에서 사용한 TFLite 사람 검출 기능을 참고한 라인트레이서용 코드.

모델 파일은 별도 실행 환경에 준비해 사용합니다.
"""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
IMAGE_PATH = str(BASE_DIR / "image" / "before.jpg")
MODEL_PATH = str(BASE_DIR / "models" / "people_detect.tflite")
MIN_CONFIDENCE = 0.2


def count_people(classes, scores):
    return sum(
        1 for cls, score in zip(classes, scores)
        if cls == 0 and score >= MIN_CONFIDENCE
    )


def detect():
    import cv2
    import numpy as np
    from tflite_runtime.interpreter import Interpreter

    image = cv2.imread(IMAGE_PATH)
    if image is None:
        raise FileNotFoundError(IMAGE_PATH)

    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    input_data = np.expand_dims(cv2.resize(rgb, (640, 640)), axis=0)

    interpreter = Interpreter(model_path=MODEL_PATH)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    if input_details[0]["dtype"] == np.float32:
        input_data = (np.float32(input_data) - 127.5) / 127.5

    if "StatefulPartitionedCall" in output_details[0]["name"]:
        classes_idx, scores_idx = 3, 0
    else:
        classes_idx, scores_idx = 1, 2

    interpreter.set_tensor(input_details[0]["index"], input_data)
    interpreter.invoke()
    classes = interpreter.get_tensor(output_details[classes_idx]["index"])[0]
    scores = interpreter.get_tensor(output_details[scores_idx]["index"])[0]
    return count_people(classes, scores)
