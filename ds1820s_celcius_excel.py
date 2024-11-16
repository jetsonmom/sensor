import serial
import pandas as pd
import datetime
import time
import os
import matplotlib.pyplot as plt
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import shutil

class TemperatureLogger:
    def __init__(self):
        # 이메일 설정
        self.email_address = "jmerrier0910@gmail.com"
        self.app_password = "smvrcqoizxbxmyhy"
        
        # 저장할 디렉토리 설정
        self.save_dir = os.path.join(os.path.expanduser("~"), "temperature_data")
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
            
        print(f"데이터 저장 경로: {self.save_dir}")
        
        # 데이터 저장용 리스트
        self.data = []
        self.current_date = datetime.datetime.now().date()
        print(f"측정 시작 시간: {datetime.datetime.now()}")
        
        # 그래프 초기화
        plt.style.use('seaborn')
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
    
    def send_daily_report(self):
        """일일 보고서 전송"""
        try:
            if len(self.data) > 0:
                # 파일명에 전날 날짜 사용
                yesterday = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y%m%d')
                excel_file = os.path.join(self.save_dir, f'temperature_log_{yesterday}.xlsx')
                
                # 데이터 저장
                df = pd.DataFrame(self.data)
                df.to_excel(excel_file, index=False)
                print(f"Excel 파일 저장 완료: {excel_file}")
                
                # 그래프 생성 및 저장
                graph_file = os.path.join(self.save_dir, f'temperature_graph_{yesterday}.png')
                if self.save_graph(graph_file):
                    # 이메일 전송
                    msg = MIMEMultipart()
                    msg['From'] = self.email_address
                    msg['To'] = self.email_address
                    msg['Subject'] = f"Temperature Log Report - {yesterday}"
                    
                    # 데이터 요약 정보
                    summary = f"""
일일 온도 측정 데이터입니다.
측정 날짜: {yesterday}
측정 기간: {df['DateTime'].iloc[0]} ~ {df['DateTime'].iloc[-1]}
데이터 수: {len(df)}개
평균 온도: {df['Temperature(°C)'].mean():.2f}°C
최고 온도: {df['Temperature(°C)'].max():.2f}°C
최저 온도: {df['Temperature(°C)'].min():.2f}°C
                    """
                    msg.attach(MIMEText(summary, 'plain'))
                    
                    # 파일 첨부
                    for filepath in [excel_file, graph_file]:
                        with open(filepath, 'rb') as f:
                            part = MIMEBase('application', 'octet-stream')
                            part.set_payload(f.read())
                            encoders.encode_base64(part)
                            part.add_header('Content-Disposition', 
                                          f'attachment; filename={os.path.basename(filepath)}')
                            msg.attach(part)
                    
                    # 이메일 전송
                    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                        server.login(self.email_address, self.app_password)
                        server.send_message(msg)
                    
                    print(f"일일 보고서 이메일 전송 완료: {datetime.datetime.now()}")
                
                # 데이터 초기화
                self.data = []
                
                # 오래된 파일 삭제
                self.clean_old_files()
                
            else:
                print("저장된 데이터가 없습니다!")
                
        except Exception as e:
            print(f"일일 보고서 처리 중 오류 발생: {e}")
    
    def save_graph(self, graph_file):
        """그래프 생성 및 저장"""
        try:
            if len(self.data) > 0:
                self.ax.clear()
                df = pd.DataFrame(self.data)
                
                self.ax.plot(pd.to_datetime(df['DateTime']), df['Temperature(°C)'], 
                            'b-', linewidth=2, label='Temperature')
                
                self.ax.set_title('Daily Temperature Monitoring', fontsize=14)
                self.ax.set_xlabel('Time', fontsize=12)
                self.ax.set_ylabel('Temperature (°C)', fontsize=12)
                self.ax.grid(True, linestyle='--', alpha=0.7)
                self.ax.legend(fontsize=10)
                
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                plt.savefig(graph_file, bbox_inches='tight', dpi=300)
                print(f"그래프 저장 완료: {graph_file}")
                return True
            return False
        except Exception as e:
            print(f"그래프 저장 중 오류 발생: {e}")
            return False
    
    def clean_old_files(self):
        """3일 이상 된 파일 삭제"""
        try:
            current_time = datetime.datetime.now()
            for file in os.listdir(self.save_dir):
                file_path = os.path.join(self.save_dir, file)
                file_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
                if (current_time - file_time).days >= 3:
                    os.remove(file_path)
                    print(f"삭제된 파일: {file}")
        except Exception as e:
            print(f"파일 삭제 중 오류 발생: {e}")
    
    def log_temperature(self):
        # Arduino 시리얼 포트 설정
        try:
            ser = serial.Serial(
                port='/dev/ttyACM0',
                baudrate=9600,
                timeout=1
            )
        except Exception as e:
            print(f"시리얼 포트 연결 실패: {e}")
            return
        
        print("온도 로깅을 시작합니다...")
        
        try:
            while True:
                current_time = datetime.datetime.now()
                current_date = current_time.date()
                
                # 날짜가 바뀌었는지 확인
                if current_date != self.current_date:
                    print("날짜가 바뀌었습니다. 일일 보고서를 생성합니다...")
                    self.send_daily_report()
                    self.current_date = current_date
                
                line = ser.readline().decode('utf-8').strip()
                
                if "Temperature =" in line:
                    try:
                        celsius = float(line.split("Temperature = ")[1].split(" Celsius")[0])
                        
                        self.data.append({
                            'DateTime': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                            'Temperature(°C)': round(celsius, 2)
                        })
                        
                        print(f"기록: {current_time.strftime('%Y-%m-%d %H:%M:%S')} - {celsius:.2f}°C (총 {len(self.data)}개)")
                    except Exception as e:
                        print(f"데이터 처리 중 오류 발생: {e}")
                        print(f"원본 데이터: {line}")
                    
        except KeyboardInterrupt:
            print("\n사용자에 의해 로깅이 중지되었습니다.")
        except Exception as e:
            print(f"오류가 발생했습니다: {e}")
        finally:
            ser.close()
            plt.close()

if __name__ == "__main__":
    logger = TemperatureLogger()
    logger.log_temperature()
