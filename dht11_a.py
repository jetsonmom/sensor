import Jetson.GPIO as GPIO
import time

# GPIO 모드를 BOARD로 설정 (물리적 핀 번호 사용)
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# DHT11 데이터 핀을 7번 핀(GPIO4)으로 설정
DHT_PIN = 7  # 물리적 7번 핀 = GPIO4

def read_dht11_dat():
    # 초기 설정
    GPIO.setup(DHT_PIN, GPIO.OUT)
    GPIO.output(DHT_PIN, GPIO.HIGH)
    time.sleep(0.05)
    
    # 센서 시작 신호
    GPIO.output(DHT_PIN, GPIO.LOW)
    time.sleep(0.02)
    GPIO.output(DHT_PIN, GPIO.HIGH)
    
    # GPIO를 입력 모드로 변경
    GPIO.setup(DHT_PIN, GPIO.IN)

    # 데이터 읽기
    data = []
    count = 0
    while GPIO.input(DHT_PIN) == GPIO.LOW:
        continue
    while GPIO.input(DHT_PIN) == GPIO.HIGH:
        continue

    for i in range(40):
        count = 0
        while GPIO.input(DHT_PIN) == GPIO.LOW:
            continue
        while GPIO.input(DHT_PIN) == GPIO.HIGH:
            count += 1
            if count > 100:
                break
        if count > 100:
            break
        data.append(0 if count < 15 else 1)

    if len(data) != 40:
        print("데이터 읽기 실패")
        return None

    # 데이터 처리
    bytes_data = []
    for i in range(5):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | data[i * 8 + j]
        bytes_data.append(byte)

    # 체크섬 확인
    if bytes_data[4] == ((bytes_data[0] + bytes_data[1] + bytes_data[2] + bytes_data[3]) & 0xFF):
        humidity = bytes_data[0]
        temperature = bytes_data[2]
        return temperature, humidity
    else:
        return None

try:
    print("DHT11 센서 읽기 시작 (물리적 7번 핀, GPIO4)")
    print("VCC: 1번 핀 (3.3V)")
    print("GND: 6번 핀")
    print("DATA: 7번 핀 (GPIO4)")
    
    while True:
        result = read_dht11_dat()
        if result is not None:
            temperature, humidity = result
            print(f'온도: {temperature}°C, 습도: {humidity}%')
        else:
            print("센서 읽기 실패, 다시 시도합니다...")
        time.sleep(2)

except KeyboardInterrupt:
    print("\n프로그램 종료")
    GPIO.cleanup()

finally:
    GPIO.cleanup()
