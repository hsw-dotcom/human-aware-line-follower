# Safe Watch 사람 검출 코드 → 라인트레이서 적용 과정: 이미지 출처 정정

## 사용자 직접 확인 (2026-10-31)

제출 사진의 용도에 대해 사용자가 명확히 정정했습니다.

> 이전에 전송한 `after.jpg` 검출 화면 및 Raspberry Pi 개발 화면은 **Safe Watch 코드에서 사람 인식 부분을 추출해 라인트레이서에 삽입하는 과정**의 기록입니다. Safe Watch 제품 자체의 최종 시연 화면으로 사용하지 않습니다.

이 증거는 프로젝트 간 **코드 재사용과 기능 통합 시도**를 설명하는 자료입니다.

## 공개 자료

| 파일 | 보이는 내용 | 허용되는 결론 |
|---|---|---|
| `assets/2023_detector_reuse_test_redacted_1.jpg` | Raspberry Pi 데스크톱의 `after.jpg` 결과·객체 박스와 프로젝트 파일 | 기존 사람 검출 코드가 라인트레이서 개발 과정에서 시험됐음 |
| `assets/2023_detector_reuse_test_redacted_2.jpg` | 여러 인물이 나타나는 이미지의 객체 검출 표시 | 사람 검출 코드 재사용·시험 과정에 관련된 화면 |
| `assets/2023_serial_test_redacted.jpg` | Geany/터미널의 Arduino–Pi 시리얼 메시지 | 개발 중 시리얼 통신 시험 화면 |

인물이 포함된 영역과 연결·계정정보를 가린 **파생 공개용 사본**입니다. 원본 이미지와 원본 코드의 정확한 실행 버전은 아직 독립적으로 일치시킬 수 없습니다.

## 주의할 점

- 위 사진들은 라인트레이서 개발 작업에 **Safe Watch의 AI 검출 경로를 재사용한 경위**를 보강합니다. Safe Watch 전체의 웹·DB·밀집도 경고 기능을 라인트레이서에 이식했다는 뜻은 아닙니다.
- **사진만으로** 실제 사람 인식 정지 성공을 검증할 수는 없습니다. 다만 사용자가 **2023년 실제 장치에서 사람 인식 시 정지 시험에 성공했다고 직접 확인**했습니다. [별도 시험·개선 기록](2023_FIELD_TEST_AND_LATENCY_IMPROVEMENT.md).
- 개발 과정에서 사용된 검출 모델의 정확도, 실제 주행 정지 성공률, 최종 Arduino/Pi 쌍의 통신 규칙은 이 사진들만으로 확정할 수 없습니다.
- 실제 과거 영상에 등장한 객체 검출 코드는 팀 프로젝트의 재사용 코드로, 기초 TFLite 모델을 사용자가 새로 학습했다고 표현하지 않습니다.
- Safe Watch 자체의 시험 화면은 [해당 프로젝트 저장소의 웹 시연 자료](https://github.com/hsw-dotcom/safe-watch-crowd-monitoring/blob/main/assets/2023_original_dashboard_capture.jpg)와 별도로 관리합니다.

## 기존 오분류의 교정

위 두 검출 화면은 최초에 Safe Watch 저장소의 `assets/2023_safewatch_detection_redacted_1.jpg`, `assets/2023_safewatch_detection_redacted_2.jpg`로 잘못 분류되어 공개됐습니다. 이후 두 파일을 Safe Watch `main`에서 제거하고 이 저장소에 용도에 맞는 이름으로 다시 추가했습니다. 과거 Git 커밋에는 삭제된 파일 이력이 남을 수 있으므로 공개 전부터 비식별 처리된 사진만 게시했다는 사실을 유지합니다.
