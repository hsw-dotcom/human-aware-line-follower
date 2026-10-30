"""Safe Watch 사람 인식 기능 추출의 대화 기반 복원본.

근거: safe-watch-crowd-monitoring/src/python/count_objects.py (보존된 원본).
원본에서 확인한 기능: TFLite Interpreter, 640x640 RGB 입력,
float32 정규화, 사람 클래스 0과 신뢰도 0.2 이상만 인원수에 포함.
라인트레이서 당시 이 파일의 실제 내용/리턴형은 보존되지 않았습니다.

Safe Watch의 장애물 분류, 박스 그리기, 웹 이미지 저장, DB, 밀집도/위험 단계는
라인트레이서 사람 존재 여부 판정에 불필요하여 의도적으로 제외했습니다.
이 파일은 OpenCV HOG를 사용하지 않습니다.
"""
from pathlib import Path
from typing import Optional, Union

MODEL_FILENAME = "people_detect.tflite"
MODEL_DIR = Path(__file__).resolve().parent.parent / "models"
DEFAULT_MODEL = MODEL_DIR / MODEL_FILENAME
DEFAULT_IMAGE = Path("runtime/before.jpg")
MODEL_IMAGE_SIZE = (640, 640)  # Safe Watch count_objects.py에서 확인된 입력 크기
PERSON_CLASS_ID = 0
MIN_CONFIDENCE = 0.2


def _count_people(classes, scores, threshold: float = MIN_CONFIDENCE) -> int:
    """당시 원본의 class==0 및 score>=0.2 판단을 분리한 순수 함수."""
    if not 0.0 <= threshold <= 1.0:
        raise ValueError("threshold must be between 0 and 1")
    if len(classes) != len(scores):
        raise ValueError("TFLite classes/scores length mismatch")
    return sum(1 for class_id, score in zip(classes, scores)
               if class_id == PERSON_CLASS_ID and float(score) >= threshold)


def _indices(output_details):
    """Safe Watch 원본의 TensorFlow Lite TF1/TF2 출력 헤드 분기."""
    if len(output_details) < 4:
        raise ValueError("expected four TFLite detection outputs")
    output_name = output_details[0]["name"]
    if "StatefulPartitionedCall" in output_name:
        return 3, 0  # classes_idx, scores_idx, TF2
    return 1, 2  # classes_idx, scores_idx, TF1


def detect(image_path: Union[str, Path] = DEFAULT_IMAGE,
           model_path: Optional[Union[str, Path]] = None) -> int:
    """이미지를 한 번 분석하여 사람 수만 반환 (원본 추출 *추정* 리턴형).

    원래 Safe Watch count_objects.detect()는 (people_num, obstacle_classes)를
    반환했지만, 사용자는 라인트레이서에서 '사람 인식만' 추출했다고 설명함.
    실제 라인트레이서 함수 시그니처/리턴형은 미확인이고, 호출부는
    detector_adapter.people_count()로 정수/2-튜플 양쪽을 수용함.
    """
    import cv2
    import numpy as np
    try:
        from tflite_runtime.interpreter import Interpreter
    except ImportError as error:
        raise ImportError("사람 검출을 위해 tflite-runtime이 필요합니다") from error

    path = Path(image_path)
    model = Path(model_path) if model_path is not None else DEFAULT_MODEL
    if not model.is_file():
        raise FileNotFoundError(
            f"Safe Watch에서 사용한 사람 감지 모델 파일이 없습니다: {model}. "
            "임의의 모델을 원본으로 표시하지 마세요.")
    frame = cv2.imread(str(path))
    if frame is None:
        raise FileNotFoundError(f"입력 이미지를 읽을 수 없습니다: {path}")

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resized = cv2.resize(rgb, MODEL_IMAGE_SIZE)
    data = np.expand_dims(resized, axis=0)

    interpreter = Interpreter(model_path=str(model))
    interpreter.allocate_tensors()
    inputs = interpreter.get_input_details()
    outputs = interpreter.get_output_details()
    if len(inputs) != 1:
        raise ValueError("expected one TFLite image input")
    in_spec = inputs[0]
    if in_spec["dtype"] == np.float32:
        data = (np.float32(data) - 127.5) / 127.5
    else:
        data = data.astype(in_spec["dtype"])
    interpreter.set_tensor(in_spec["index"], data)
    interpreter.invoke()

    classes_idx, scores_idx = _indices(outputs)
    classes = interpreter.get_tensor(outputs[classes_idx]["index"])[0]
    scores = interpreter.get_tensor(outputs[scores_idx]["index"])[0]
    return _count_people(classes, scores)
