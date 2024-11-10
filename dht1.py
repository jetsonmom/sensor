import time
import board
import adafruit_dht

# DHT11 센서 초기화 (GPIO4 사용)
dht = adafruit_dht.DHT11(board.D4)

def read_sensor():
    try:
        temperature = dht.temperature
        humidity = dht.humidity
        
        if temperature is not None and humidity is not None:
            print(f"온도: {temperature:.1f}°C")
            print(f"습도: {humidity:.1f}%")
        else:
            print("센서 읽기 실패")
            
    except RuntimeError as error:
        print(f"에러: {error.args[0]}")
    except Exception as error:
        dht.exit()
        raise error

print("DHT11 센서 읽기 시작...")
print("Ctrl+C를 눌러서 프로그램 종료")

try:
    while True:
        read_sensor()
        time.sleep(2.0)
        
except KeyboardInterrupt:
    print("\n프로그램 종료")
    
finally:
    dht.exit()
