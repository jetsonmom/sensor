import serial
import pandas as pd
import datetime
import time

def log_temperature():
    # Arduino 시리얼 포트 설정
    ser = serial.Serial(
        port='/dev/ttyACM0',
        baudrate=9600,
        timeout=1
    )
    
    # 데이터를 저장할 리스트
    data = []
    
    print("온도 로깅을 시작합니다...")
    print("종료하려면 Ctrl+C를 누르세요.")
    
    try:
        while True:
            # 시리얼 데이터 읽기
            line = ser.readline().decode('utf-8').strip()
            
            # 온도 데이터가 포함된 줄 찾기
            if "Temperature =" in line:
                # 현재 시간
                current_time = datetime.datetime.now()
                
                # 온도값 추출
                celsius = float(line.split("Temperature = ")[1].split(" Celsius")[0])
                
                # 데이터 저장
                data.append({
                    'DateTime': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                    'Temperature(°C)': round(celsius, 2)
                })
                
                # DataFrame 생성 및 Excel 파일로 저장
                df = pd.DataFrame(data)
                df.to_excel('temperature_log.xlsx', index=False)
                
                print(f"기록: {current_time.strftime('%Y-%m-%d %H:%M:%S')} - {celsius:.2f}°C")
                
    except KeyboardInterrupt:
        print("\n사용자에 의해 로깅이 중지되었습니다.")
        print(f"총 {len(data)}개의 데이터가 저장되었습니다.")
        ser.close()
    except Exception as e:
        print(f"오류가 발생했습니다: {e}")
        ser.close()

if __name__ == "__main__":
    log_temperature()
