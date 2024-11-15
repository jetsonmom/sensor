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
        self.email_address = ""
        self.app_password = ""
        
        # 저장할 디렉토리 설정
        self.save_dir = "/home/jetson/temperature_data"
        if not os.path.exists(self.save_dir):
            os.makedirs(self.save_dir)
        
        # 데이터 저장용 리스트
        self.data = []
        self.start_time = datetime.datetime.now()
        
        # 그래프 초기화
        plt.style.use('seaborn')
        self.fig, self.ax = plt.subplots(figsize=(12, 6))
        
    def clean_old_files(self):
        """3일 이상 된 파일 삭제"""
        current_time = datetime.datetime.now()
        for file in os.listdir(self.save_dir):
            file_path = os.path.join(self.save_dir, file)
            file_time = datetime.datetime.fromtimestamp(os.path.getctime(file_path))
            if (current_time - file_time).days >= 3:
                os.remove(file_path)
                print(f"삭제된 파일: {file}")
    
    def send_email(self, excel_file, graph_file):
        """이메일 전송"""
        msg = MIMEMultipart()
        msg['From'] = self.email_address
        msg['To'] = self.email_address
        msg['Subject'] = f"Temperature Log Report - {datetime.datetime.now().strftime('%Y-%m-%d')}"
        
        body = "24시간 온도 측정 데이터입니다.\n첨부된 파일을 확인해주세요."
        msg.attach(MIMEText(body, 'plain'))
        
        # Excel 파일 첨부
        with open(excel_file, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 
                          f'attachment; filename={os.path.basename(excel_file)}')
            msg.attach(part)
        
        # 그래프 이미지 첨부
        with open(graph_file, 'rb') as f:
            part = MIMEBase('application', 'octet-stream')
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 
                          f'attachment; filename={os.path.basename(graph_file)}')
            msg.attach(part)
        
        # 이메일 전송
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(self.email_address, self.app_password)
            server.send_message(msg)
        
        print("이메일이 전송되었습니다.")
    
    def save_graph(self):
        """그래프를 이미지로 저장"""
        self.update_plot()
        graph_file = os.path.join(self.save_dir, 
                                 f'temperature_graph_{datetime.datetime.now().strftime("%Y%m%d")}.png')
        plt.savefig(graph_file)
        return graph_file
    
    def update_plot(self):
        """그래프 업데이트"""
        if len(self.data) > 0:
            self.ax.clear()
            df = pd.DataFrame(self.data)
            
            self.ax.plot(pd.to_datetime(df['DateTime']), df['Temperature(°C)'], 
                        'b-', linewidth=2, label='Temperature')
            
            self.ax.set_title('24-Hour Temperature Monitoring', fontsize=14, pad=20)
            self.ax.set_xlabel('Time', fontsize=12)
            self.ax.set_ylabel('Temperature (°C)', fontsize=12)
            self.ax.grid(True, linestyle='--', alpha=0.7)
            self.ax.legend(fontsize=10)
            
            plt.xticks(rotation=45)
            plt.tight_layout()
    
    def log_temperature(self):
        # Arduino 시리얼 포트 설정
        ser = serial.Serial(
            port='/dev/ttyACM0',
            baudrate=9600,
            timeout=1
        )
        
        print("온도 로깅을 시작합니다...")
        
        try:
            while True:
                current_time = datetime.datetime.now()
                
                # 24시간이 지났는지 확인
                if (current_time - self.start_time).days >= 1:
                    excel_file = os.path.join(self.save_dir, 
                                            f'temperature_log_{self.start_time.strftime("%Y%m%d")}.xlsx')
                    df = pd.DataFrame(self.data)
                    df.to_excel(excel_file, index=False)
                    
                    graph_file = self.save_graph()
                    self.send_email(excel_file, graph_file)
                    
                    # 새로운 24시간 주기 시작
                    self.start_time = current_time
                    self.data = []
                    
                    # 오래된 파일 삭제
                    self.clean_old_files()
                
                line = ser.readline().decode('utf-8').strip()
                
                if "Temperature =" in line:
                    celsius = float(line.split("Temperature = ")[1].split(" Celsius")[0])
                    
                    self.data.append({
                        'DateTime': current_time.strftime('%Y-%m-%d %H:%M:%S'),
                        'Temperature(°C)': round(celsius, 2)
                    })
                    
                    print(f"기록: {current_time.strftime('%Y-%m-%d %H:%M:%S')} - {celsius:.2f}°C")
                    
        except KeyboardInterrupt:
            print("\n사용자에 의해 로깅이 중지되었습니다.")
            ser.close()
            plt.close()
        except Exception as e:
            print(f"오류가 발생했습니다: {e}")
            ser.close()
            plt.close()

if __name__ == "__main__":
    logger = TemperatureLogger()
    logger.log_temperature()
