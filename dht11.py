import Jetson.GPIO as GPIO
import time

# GPIO 모드를 BOARD로 설정
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# DHT11 데이터 핀 설정 (7번 핀)
DHT_PIN = 7

def read_dht11_dat():
    # 타임아웃 설정
    timeout = time.time() + 0.5  # 0.5초 타임아웃
    
    # 초기 설정
    GPIO.setup(DHT_PIN, GPIO.OUT)
    GPIO.output(DHT_PIN, GPIO.HIGH)
    time.sleep(0.05)
    
    # 센서 시작 신호
    GPIO.output(DHT_PIN, GPIO.LOW)
    time.sleep(0.018)  # 18ms 대기
    GPIO.output(DHT_PIN, GPIO.HIGH)
    time.sleep(0.00004)  # 40μs 대기
    
    # GPIO를 입력 모드로 변경
    GPIO.setup(DHT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # 데이터 읽기 준비
    data = []
    last = -1
    bits = 0
    value = 0

    # DHT11 응답 대기
    while GPIO.input(DHT_PIN) == GPIO.HIGH:
        if time.time() > timeout:
            print("센서 응답 없음 (타임아웃)")
            return None
        continue

    while bits < 40:
        count = 0
        while GPIO.input(DHT_PIN) == last:
            count += 1
            if count > 100 or time.time() > timeout:
                print(f"비트 {bits} 읽기 실패")
                return None
            time.sleep(0.000001)
        last = GPIO.input(DHT_PIN)
        
        if count > 16:
            value = (value << 1) | 1
        else:
            value = value << 1
            
        bits += 1
        if bits % 8 == 0:
            data.append(value)
            value = 0

    if len(data) != 5:
        print(f"잘못된 데이터 길이: {len(data)}")
        return None

    # 체크섬 확인
    if data[4] == ((data[0] + data[1] + data[2] + data[3]) & 0xFF):
        humidity = data[0]
        temperature = data[2]
        return temperature, humidity
    else:
        print("체크섬 오류")
        return None

try:
    print("\nDHT11 센서 테스트 시작")
    print("연결 상태:")
    print("VCC: 2번 핀 (5V로 변경)")
    print("GND: 6번 핀")
    print("DATA: 7번 핀 (GPIO4)")
    print("센서 초기화 중...\n")
    time.sleep(2)  # 센서 안정화 대기
    
    while True:
        result = read_dht11_dat()
        if result is not None:
            temperature, humidity = result
            print(f'온도: {temperature}°C, 습도: {humidity}%')
        else:
            print("재시도 중...")
        time.sleep(2)

except KeyboardInterrupt:
    print("\n프로그램 종료")
    GPIO.cleanup()

finally:
    GPIO.cleanup()
