# Safe Watch 사람 인식 코드 재사용 — 실제 사용자 설명 반영

## 확인된 사실

- 사용자는 라인트레이서에서 별도의 사람 인식기를 새로 개발한 것이 아니라 **Safe Watch(군중 밀집도 감지 카메라)의 사람 인식 기능 중 필요한 부분만 추출하여 재사용**했다고 설명했습니다.
- Safe Watch에 보존된 `src/python/count_objects.py` 원본은 `tflite_runtime.interpreter.Interpreter`로 `models/people_detect.tflite`를 실행합니다.
- Safe Watch 원본에서 확인되는 입력과 판정은 640×640 RGB, float32 모델 입력 정규화 `(input - 127.5)/127.5`, `class == 0`, `confidence >= 0.2`입니다.
- Safe Watch의 원본 `detect()`는 `(people_num, obstacle_classes)`를 반환합니다. 장애물 검출부는 호출이 비활성화되어 있습니다.
- 라인트레이서 대화에서는 `before.jpg` 촬영 후 `count_objects.detect()` 호출 및 사람 수에 따라 `0/1`을 판단하는 흐름이 확인됩니다.

## 라인트레이서 복원 방식

`raspberry_pi/line_tracer/count_objects.py`는 Safe Watch 원본 **사람 검출 계산 경로**를 근거로, 필요 없던 기능을 제외한 복원 코드입니다.

| Safe Watch 기능 | 라인트레이서 복원본에서 |
|---|---|
| 사람 모델 실행 및 수 계산 | 유지 (TFLite) |
| 이미지 촬영 및 저장 | 카메라 모듈에서 `before.jpg`로 유지 |
| 장애물 탐지 | 제외 |
| 바운딩 박스·텍스트·`after.jpg` 웹 출력 | 제외 |
| 밀집도, 경고단계 계산 | 제외 |
| MariaDB/PHP/AJAX/웹 대시보드 | 제외 |
| 반환값 | **정수 인원수로 추정**, 당시 라인트레이서 원본의 정확한 반환형은 미확인 |

## 여전히 미확인

- 당시 라인트레이서에 가져온 `count_objects.py` 파일의 정확한 변경 줄, 함수명·반환값, 모델 경로 및 카메라 이미지 경로.
- `people_detect.tflite` 실제 모델 가중치 파일 및 사용 버전.
- 실제 3~5m 거리 검출 성능과 정확도 수치.

이 저장소의 코드는 2023년 라인트레이서 원본 **그 자체가 아닙니다**. 다만 사람 인식 알고리즘의 출처는 더 이상 HOG 임의 대체가 아니라, 보존된 Safe Watch 소스를 근거로 특정할 수 있습니다.

원본 근거:
- https://github.com/hsw-dotcom/safe-watch-crowd-monitoring/blob/main/src/python/count_objects.py
- https://github.com/hsw-dotcom/safe-watch-crowd-monitoring/blob/main/src/python/main.py

## 3자 코드 출처 및 역할

Safe Watch 보존 소스의 머리말에는 TensorFlow Lite 예제를 기반으로 변형한 작성자 **Evan Juras**가 명시되어 있습니다. 라인트레이서에서의 본인 개발 기여는 기존 사람 인식 모듈의 필요한 부분을 선택·적용하고 Arduino 정지 제어와 연결한 것입니다. **기초 객체 감지기 구현이나 모델 학습을 새로 수행한 것으로 표현하지 않습니다.** 원본의 라이선스와 재배포 조건은 별도 확인이 필요하므로 Safe Watch 원본을 통째로 복사하지 않고 기능을 참조해 다시 작성했습니다.
