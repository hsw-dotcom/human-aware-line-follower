# 모델 파일 위치 (미확보)

Safe Watch 원본 `src/python/count_objects.py`에는 `models/people_detect.tflite`가 지정되어 있습니다. 라인트레이서도 이 모델 계열의 **사람 인식 기능만 추출해 재사용**했다는 것이 사용자 설명입니다.

아래 파일은 이 저장소에서 확보하지 못했으므로 임의 생성하거나 다른 모델로 대체하지 않습니다.

- `people_detect.tflite` — Safe Watch 원본 코드가 가리키는 사람 검출 모델 가중치
- `people_label.txt` — 원본 Safe Watch에서 박스 라벨 표시용으로 사용 (이 복원본은 표시 기능 제거로 불필요)

코드 복원 및 순수 함수 테스트에는 모델 파일이 필요하지 않습니다. 실제 모델 추론 호출에는 파일이 필요합니다.

참조: https://github.com/hsw-dotcom/safe-watch-crowd-monitoring/blob/main/src/python/count_objects.py
