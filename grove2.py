import Jetson.GPIO as GPIO
import time

# GPIO 설정
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
PIN = 12  # 12번 핀으로 변경 (GPIO18)

def setup():
    GPIO.setup(PIN, GPIO.IN)
    print("GPIO 초기화 완료")

def main():
    # 원본 변수명 그대로 사용
    duration = 0
    lowpulseoccupancy = 0
    starttime = time.time() * 1000
    sampletime_ms = 30000  # 30초
    
    print("\n=== 먼지 센서 모니터링 ===")
    print("연결: ")
    print(f"VCC → 5V (2번 핀)")
    print(f"GND → GND (6번 핀)")
    print(f"DATA → GPIO (12번 핀)")
    print("\n30초마다 데이터 출력")
    print("형식: lowpulseoccupancy,ratio,concentration")
    
    try:
        while True:
            # LOW 신호 지속 시간 측정
            if GPIO.input(PIN) == GPIO.LOW:
                duration = time.time() * 1000
                while GPIO.input(PIN) == GPIO.LOW:
                    time.sleep(0.0001)
                duration = (time.time() * 1000) - duration
                lowpulseoccupancy += duration
            
            # 30초마다 계산 및 출력
            current_time = time.time() * 1000
            if (current_time - starttime) > sampletime_ms:
                ratio = lowpulseoccupancy / (sampletime_ms * 10.0)
                concentration = 1.1 * pow(ratio, 3) - 3.8 * pow(ratio, 2) + 520 * ratio + 0.62
                # 값이 너무 커서 수정이 필요. concentration = 0.1*pow(ratio,3) - 0.38*pow(ratio,2) + 52*ratio + 0.62;로 보정. 
                # 원본과 동일한 출력 형식
                print(f"{int(lowpulseoccupancy)},{ratio:.2f},{concentration:.2f}")
                
                lowpulseoccupancy = 0
                starttime = current_time
            
            time.sleep(0.001)
            
    except KeyboardInterrupt:
        print("\n프로그램 종료")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    setup()
    main()
