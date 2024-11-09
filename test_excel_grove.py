import Jetson.GPIO as GPIO
import time
from datetime import datetime
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os

# GPIO 설정
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
PIN = 12

# 이메일 설정
email_address = "aaaaaaa@gmail.com"
app_password = "aaaaaaaaaaaaaa"

def setup():
    GPIO.setup(PIN, GPIO.IN)
    print("GPIO 초기화 완료")

def send_email(data):
    try:
        # 엑셀 파일 생성
        df = pd.DataFrame(data)
        filename = f"dust_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(filename, index=False)

        # 이메일 메시지 생성
        message = MIMEMultipart()
        message["From"] = email_address
        message["To"] = email_address
        message["Subject"] = f"먼지 센서 데이터 ({datetime.now().strftime('%H:%M:%S')})"

        # 이메일 본문
        body = f"""
        먼지 센서 측정 데이터입니다.
        측정 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        먼지 농도: {data[-1]['concentration']:.2f} μg/m³
        """
        message.attach(MIMEText(body, 'plain'))

        # 파일 첨부
        with open(filename, "rb") as attachment:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(attachment.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f"attachment; filename= {filename}")
            message.attach(part)

        # 이메일 전송
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(email_address, app_password)
            server.send_message(message)

        print(f"이메일 전송 완료: {filename}")
        
        # 파일 삭제
        os.remove(filename)
        return True
    
    except Exception as e:
        print(f"이메일 전송 실패: {e}")
        return False

def main():
    dust_data = []
    duration = 0
    lowpulseoccupancy = 0
    starttime = time.time() * 1000
    measurement_count = 0
    
    print("\n=== 먼지 센서 모니터링 및 이메일 전송 ===")
    print(f"측정 및 이메일 전송: 30초마다")
    print(f"이메일 주소: {email_address}")
    print("\n측정 시작...")
    
    try:
        while True:
            if GPIO.input(PIN) == GPIO.LOW:
                duration = time.time() * 1000
                while GPIO.input(PIN) == GPIO.LOW:
                    time.sleep(0.0001)
                duration = (time.time() * 1000) - duration
                lowpulseoccupancy += duration
            
            current_time = time.time() * 1000
            if (current_time - starttime) > 30000:  # 30초마다
                measurement_count += 1
                ratio = lowpulseoccupancy / (30000 * 10.0)
                concentration = 1.1 * pow(ratio, 3) - 3.8 * pow(ratio, 2) + 520 * ratio + 0.62
                
                current_datetime = datetime.now()
                
                # 데이터 저장
                dust_data.append({
                    'timestamp': current_datetime.strftime('%Y-%m-%d %H:%M:%S'),
                    'lowpulseoccupancy': int(lowpulseoccupancy),
                    'ratio': round(ratio, 2),
                    'concentration': round(concentration, 2)
                })
                
                print(f"\n[측정 #{measurement_count}]")
                print(f"시간: {current_datetime.strftime('%H:%M:%S')}")
                print(f"먼지 농도: {concentration:.2f} μg/m³")
                
                # 즉시 이메일 전송
                print("이메일 전송 중...")
                if send_email([dust_data[-1]]):  # 최신 데이터만 전송
                    print("전송 성공")
                else:
                    print("전송 실패")
                
                # 변수 초기화
                lowpulseoccupancy = 0
                starttime = current_time
            
            time.sleep(0.001)
            
    except KeyboardInterrupt:
        print("\n\n프로그램 종료")
        if dust_data:
            print("최종 데이터 전송 중...")
            send_email([dust_data[-1]])
    
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    setup()
    main()
