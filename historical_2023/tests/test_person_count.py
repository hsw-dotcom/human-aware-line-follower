"""모델/카메라 없이 원본 TFLite 감지의 선별 규칙만 확인."""
import sys
import unittest
from pathlib import Path
from types import ModuleType
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'raspberry_pi'))
# 라이브러리 설치 없이 순수 규칙만 테스트하기 위한 최소 가상 모듈.
cv=ModuleType('cv2'); np=ModuleType('numpy')
tflite=ModuleType('tflite_runtime'); interpreter=ModuleType('tflite_runtime.interpreter')
interpreter.Interpreter=object
for key, mod in [('cv2',cv),('numpy',np),('tflite_runtime',tflite),('tflite_runtime.interpreter',interpreter)]:
    sys.modules.setdefault(key,mod)
import count_objects

class PersonCountTests(unittest.TestCase):
    def test_threshold_class(self):
        self.assertEqual(count_objects.count_people([0,0,1,0],[.2,.19,1,.8]), 2)
    def test_no_person(self):
        self.assertEqual(count_objects.count_people([1,1],[.99,.9]), 0)
        self.assertEqual(count_objects.count_people([],[]), 0)
    def test_safe_watch_parameters(self):
        self.assertEqual((count_objects.WIDTH,count_objects.HEIGHT),(640,640))
        self.assertEqual(count_objects.MIN_CONFIDENCE,0.2)

if __name__=='__main__': unittest.main()
