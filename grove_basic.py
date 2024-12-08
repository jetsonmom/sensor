import time
import RPi.GPIO as GPIO
import math

class DustSensor:
    def __init__(self, pin=8):
        # GPIO 설정
        self.pin = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN)
        
        # 변수 초기화
        self.sampletime_ms = 3000  # 3초
        self.lowpulseoccupancy = 0
        self.starttime = time.time() * 1000  # 밀리초 단위로 변환

    def read_dust(self):
        # pulseIn 함수 구현 (LOW 신호의 지속 시간 측정)
        def pulse_in(pin, level, timeout=1.0):
            start_time = time.time()
            while GPIO.input(pin) != level:
                if (time.time() - start_time) >= timeout:
                    return 0
            start_while = time.time()
            while GPIO.input(pin) == level:
                if (time.time() - start_while) >= timeout:
                    return 0
            pulse_time = (time.time() - start_while) * 1000000  # 마이크로초 단위
            return pulse_time

        try:
            while True:
                # LOW 신호 지속 시간 측정
                duration = pulse_in(self.pin, GPIO.LOW)
                self.lowpulseoccupancy += duration

                # 샘플링 시간 체크
                current_time = time.time() * 1000
                if (current_time - self.starttime) >= self.sampletime_ms:
                    # 비율 계산
                    ratio = self.lowpulseoccupancy / (self.sampletime_ms * 10.0)
                    
                    # 미세먼지 농도 계산
                    concentration = (1.1 *  pow(ratio, 3) - 
                                  3.8 *  pow(ratio, 2) + 
                                  520 *  ratio + 0.62)
                    
                    # µg/m³ 단위로 변환
                    pm25_particles_per_liter = concentration / 300

                    # 결과 출력
                    print(f"concentration = {concentration:.2f} pcs/0.01cf")
                    print(f"dust = {pm25_particles_per_liter:.2f} ug/m3\n")

                    # 변수 초기화
                    self.lowpulseoccupancy = 0
                    self.starttime = time.time() * 1000

                time.sleep(0.001)  # CPU 부하 감소

        except KeyboardInterrupt:
            print("\nMeasurement stopped by user")
            GPIO.cleanup()
        except Exception as e:
            print(f"Error: {e}")
            GPIO.cleanup()

if __name__ == "__main__":
    try:
        sensor = DustSensor(pin=8)
        sensor.read_dust()
    finally:
        GPIO.cleanup()
