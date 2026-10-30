"""Safe Watch의 사람 검출 부분만 추린 '라인트레이서용' 복원 함수.

원본 출처: safe-watch-crowd-monitoring/src/python/count_objects.py
- 640x640 RGB, TFLite, float 입력 정규화 (127.5/127.5),
  class==0, confidence>=0.2를 원본 코드에서 확인.
- 장애물, 화면 박스 그리기, after.jpg 저장, DB 관련 기능은 추출 대상에서 제외.
- **당시 라인트레이서에서 사용한 정확한 파일과 반환형은 미확인.**
  '사람 인식만 추출' 진술에 맞추어 이 복원은 사람 수 정수만 반환.
- TensorFlow Lite 학습 모델과 라벨 파일은 보존되지 않아 포함하지 않음.
"""
WIDTH, HEIGHT = 640, 640
MIN_CONFIDENCE = 0.2
IMAGE_PATH = '/home/pi/project/image/before.jpg'  # Safe Watch 원본 경로, 라인트레이서 여부 미확인
MODEL_PATH = 'models/people_detect.tflite'


def count_people(classes, scores):
    people_num = 0
    for i in range(len(scores)):
        if scores[i] >= MIN_CONFIDENCE and classes[i] == 0:
            people_num += 1
    return people_num


def detect():
    # 외부 의존성은 실제 영상 검출 시에만 읽습니다 (오프라인 테스트 가능).
    import cv2
    import numpy as np
    from tflite_runtime.interpreter import Interpreter
    image = cv2.imread(IMAGE_PATH)
    if image is None:
        raise FileNotFoundError(IMAGE_PATH)

    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    image_resized = cv2.resize(image_rgb, (WIDTH, HEIGHT))
    input_data = np.expand_dims(image_resized, axis=0)

    interpreter = Interpreter(model_path=MODEL_PATH)
    interpreter.allocate_tensors()
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    if input_details[0]['dtype'] == np.float32:
        input_data = (np.float32(input_data) - 127.5) / 127.5

    # Safe Watch 원본의 TF1 / TF2 텐서 위치 분기 그대로 유지.
    if 'StatefulPartitionedCall' in output_details[0]['name']:
        boxes_idx, classes_idx, scores_idx = 1, 3, 0
    else:
        boxes_idx, classes_idx, scores_idx = 0, 1, 2

    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    people_classes = interpreter.get_tensor(output_details[classes_idx]['index'])[0]
    people_scores = interpreter.get_tensor(output_details[scores_idx]['index'])[0]

    return count_people(people_classes, people_scores)
