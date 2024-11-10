#센서값　이메일　전송

import Jetson.GPIO as GPIO
import time
from datetime import datetime, timedelta
import pandas as pd
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os
import glob

# GPIO 설정
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)
PIN = 12

# 이메일 설정
email_address = "jmerrier0910@gmail.com"
app_password = "xxxxxxxxxxx"

def setup():
    GPIO.setup(PIN, GPIO.IN)
    print("GPIO 초기화 완료")

def cleanup_old_files():
    """3일 이상 된 파일 삭제"""
    try:
        current_time = datetime.now()
        file_pattern = "dust_data_*.xlsx"
        for file in glob.glob(file_pattern):
            # 파일 생성 시간 확인
            file_time = datetime.fromtimestamp(os.path.getctime(file))
            # 3일 이상 된 파일 삭제
            if (current_time - file_time).days >= 3:
                os.remove(file)
                print(f"오래된 파일 삭제: {file}")
    except Exception as e:
        print(f"파일 정리 중 오류 발생: {e}")

def send_email(data):
    try:
        # 엑셀 파일 생성
        df = pd.DataFrame(data)
        filename = f"dust_data_{datetime.now().strftime('%Y%m%d')}.xlsx"
        df.to_excel(filename, index=False)

        # 이메일 메시지 생성
        message = MIMEMultipart()
        message["From"] = email_address
        message["To"] = email_address
        message["Subject"] = f"일일 먼지 센서 데이터 ({datetime.now().strftime('%Y-%m-%d')})"

        # 통계 계산
        avg_concentration = sum(d['concentration'] for d in data) / len(data)
        max_concentration = max(d['concentration'] for d in data)
        min_concentration = min(d['concentration'] for d in data)

        # 이메일 본문
        body = f"""
        일일 먼지 센서 측정 리포트

        측정 일자: {datetime.now().strftime('%Y-%m-%d')}
        총 측정 횟수: {len(data)}회
        
        통계:
        - 평균 농도: {avg_concentration:.2f} μg/m³
        - 최대 농도: {max_concentration:.2f} μg/m³
        - 최소 농도: {min_concentration:.2f} μg/m³
        
        * 모든 데이터는 3일 후 자동으로 삭제됩니다.
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

        print(f"\n일일 리포트 이메일 전송 완료: {filename}")
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
    last_email_date = datetime.now().date()
    last_cleanup_time = datetime.now()
    
    print("\n=== 먼지 센서 모니터링 시스템 (일일 리포트) ===")
    print(f"측정: 30초마다")
    print(f"이메일 전송: 매일 자정")
    print(f"데이터 보관: 3일")
    print(f"이메일 주소: {email_address}")
    print("\n측정 시작...")
    
    try:
        while True:
            current_datetime = datetime.now()
            
            # 매일 한 번 오래된 파일 정리
            if (current_datetime - last_cleanup_time).days >= 1:
                print("\n오래된 파일 정리 중...")
                cleanup_old_files()
                last_cleanup_time = current_datetime
            
            if GPIO.input(PIN) == GPIO.LOW:
                duration = time.time() * 1000
                while GPIO.input(PIN) == GPIO.LOW:
                    time.sleep(0.0001)
                duration = (time.time() * 1000) - duration
                lowpulseoccupancy += duration
            
            current_time = time.time() * 1000
            current_date = current_datetime.date()
            
            # 30초마다 측정
            if (current_time - starttime) > 30000:
                measurement_count += 1
                ratio = lowpulseoccupancy / (30000 * 10.0)
                concentration = 1.1 * pow(ratio, 3) - 3.8 * pow(ratio, 2) + 520 * ratio + 0.62
                
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
                
                # 날짜가 바뀌었는지 확인
                if current_date != last_email_date:
                    print("\n새로운 날짜 감지 - 일일 리포트 전송 중...")
                    if dust_data:
                        if send_email(dust_data):
                            dust_data = []  # 데이터 초기화
                            measurement_count = 0
                    last_email_date = current_date
                
                # 변수 초기화
                lowpulseoccupancy = 0
                starttime = current_time
            
            time.sleep(0.001)
            
    except KeyboardInterrupt:
        print("\n\n프로그램 종료")
        if dust_data:
            print("최종 데이터 전송 중...")
            send_email(dust_data)
    
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    setup()
    main()
