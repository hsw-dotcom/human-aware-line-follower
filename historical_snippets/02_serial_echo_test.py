import serial
import time

# 시리얼 포트 설정
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)

try:
    while True:
        # 아두이노에서 데이터 읽기
        data = ser.readline().decode('utf-8').strip()
        
        if data:
            print(f"Received from Arduino: {data}")
        
        # 라즈베리 파이에서 데이터 보내기 (예: "Hello from Raspberry Pi!")
        message_to_send = "Hello from Raspberry Pi!"
        ser.write(message_to_send.encode())
        
        time.sleep(1)

except KeyboardInterrupt:
    print("프로그램을 종료합니다.")
finally:
    # 시리얼 포트 닫기
    ser.close()
