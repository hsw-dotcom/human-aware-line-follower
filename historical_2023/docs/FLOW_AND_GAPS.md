# 2023년 대화에서 역추적할 수 있는 기능 흐름

```text
Arduino IR센서 → 라인 추종
            ↘ TCS34725 색상 / 버튼 상태
             Arduino 송신: r:g:b:button
                         ↓
                Raspberry Pi 수신
                         ↓
             필요한 구간에서 카메라 촬영
                  image/before.jpg
                         ↓
            Safe Watch에서 추출한
                count_objects.detect()
                         ↓
             people_num + RGB + button
                         ↓
             result(0 또는 1) 회신
                         ↓
            Arduino 정지 / 라인 추종
```

## 판단식과 설명 사이에 남아 있는 불일치

- **색 구간이 탐지되는 순간 `result=0`인 원식**이라 사람 존재 여부와 관계없이
  색 구간에서 정지합니다. 이를 `색 구간 AND 사람`으로 임의 수정하면 대화의
  최종 조건식을 위반하므로 수정하지 않았습니다.
- RGB 변환식이 없으므로 `getRGB()` 출력을 정수화한 예시 Arduino와 Python의
  임계값이 실제 바닥색을 분류한다고 보장할 수 없습니다.
- `people_num`을 실제로 모든 구간마다 갱신했는지, 지정된 색 구간에서만 갱신했는지
  원본 코드 없이는 확정할 수 없습니다. 복원본은 '특정 구간에서 사람 인식'이라는
  개발 설명을 근거로 해당 조건에서 촬영합니다.
- Safe Watch 원본은 검출 결과로 `(people_num, obstacle_classes)`를 반환했지만,
  라인트레이서에서 필요한 기능만 추출했다는 설명에 따라 정수형 사람 수만 반환하도록
  축약했습니다. 당시 함수의 반환형은 미확인입니다.

### 외부 코드 출처
Safe Watch의 감지 함수는 역사적으로 Evan Juras의 TensorFlow Lite 예제에서 유래했고
사용자가 프로젝트에 맞게 적용했던 코드입니다. 이 복원에서는 직접 확인한 사람 검출 단계만 유지했습니다.
