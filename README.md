#  ds1820s temp sensor

![image](https://github.com/user-attachments/assets/ea840679-0ecc-4138-a7ab-7be90d25e6b7)
![image](https://github.com/user-attachments/assets/c03631c6-7399-44fa-b250-2f5411a1dc05)

##plegable terminal 


![image](https://github.com/user-attachments/assets/e08cf3f7-3fcd-4e66-88f7-0ea15fd69789)




<b>arduino -> lib

onwire lib install


circuit

![image](https://github.com/user-attachments/assets/16413b94-dc48-47f5-9c77-1aa842f2b0a7)



## ds1820s test  data 1day--> gmail send

dli@dli-desktop:~$ python3 ds1820s_celcius.py

온도 로깅을 시작합니다...

기록: 2024-11-15 20:37:18 - 21.31°C

기록: 2024-11-15 20:47:19 - 21.31°C

기록: 2024-11-15 20:57:20 - 21.37°C



<b>  co2
이 이미지는 센서의 UART 통신 핀 배열을 보여주고 있습니다. UART 방식으로 연결하려면 다음과 같이 연결하시면 됩니다:

```
센서            Arduino
UART TX   →    D2 (RX)
UART RX   →    D3 (TX)
GND       →    GND
5V 입력   →    5V
```

추가 핀들:
- CA, RT: 보정용 핀으로 일반적으로 사용하지 않음
- PWM, A: 아날로그/PWM 출력 핀으로 선택적 사용
- 3.3V 옵션: 3.3V 로직을 사용하는 경우

아두이노 코드는 다음과 같이 작성할 수 있습니다:

```cpp
#include <SoftwareSerial.h>

// UART 통신용 핀 정의
#define SENSOR_RX_PIN 2  // 센서의 TX와 연결
#define SENSOR_TX_PIN 3  // 센서의 RX와 연결

SoftwareSerial sensorSerial(SENSOR_RX_PIN, SENSOR_TX_PIN);

void setup() {
  // 디버깅을 위한 시리얼 통신 시작
  Serial.begin(9600);
  
  // 센서와의 UART 통신 시작
  sensorSerial.begin(9600);
  
  Serial.println("CO2 센서 초기화 중...");
  delay(1000);
}

void loop() {
  if (sensorSerial.available()) {
    // 센서로부터 데이터 읽기
    while (sensorSerial.available()) {
      char c = sensorSerial.read();
      Serial.write(c);  // 디버깅을 위해 시리얼 모니터로 출력
    }
  }
  
  delay(1000);  // 1초 대기
}

```

주의사항:
1. TX와 RX는 교차 연결해야 합니다 (센서 TX → 아두이노 RX, 센서 RX → 아두이노 TX)
2. 전원은 반드시 5V를 사용하세요
3. GND는 반드시 연결해야 합니다
4. 시리얼 통신 속도는 9600bps로 설정되어 있습니다

필요한 경우 추가적인 설정이나 코드 수정을 도와드릴 수 있습니다.

기록: 2024-11-15 21:07:22 - 21.31°C

# co2 sensor
비분산 적외선 방식.
이산화탄소가 흡수하는 적외선의 주파수를 쏘고 이산화탄소에 흡수되지 않는 적외선 양을 측정.  #출처 에듀이노

![image](https://github.com/user-attachments/assets/d89ae521-d5fc-43ed-87cc-bde22ae80026)


![image](https://github.com/user-attachments/assets/73ca24e7-6bfd-40ff-b6a7-b45939d5b4f7)

## 핀맵
![image](https://github.com/user-attachments/assets/e15063dc-ae83-4533-8e85-a4e517dda387)

![image](https://github.com/user-attachments/assets/74511674-ef24-40c2-b67d-d0b7c703a241)



<b>  시리얼 포트를 찾지 못하는 에러네요. 먼저 연결된 시리얼 포트를 확인해보겠습니다.

1. 연결된 시리얼 포트 확인:
```bash
ls /dev/tty*
```
또는
```bash
dmesg | grep tty
```

2. USB 장치 확인:
```bash
lsusb
```

3. 권한 설정:
```bash
sudo usermod -a -G dialout $USER
sudo chmod 666 /dev/ttyACM0  # 또는 실제 포트 이름
```

수정된 코드:

```python
import serial
import time
import requests
import json
from datetime import datetime
import glob
import sys

def find_serial_port():
    """사용 가능한 시리얼 포트 찾기"""
    ports = glob.glob('/dev/tty[A-Za-z]*')
    available_ports = []
    
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            available_ports.append(port)
        except (OSError, serial.SerialException):
            pass
    
    if not available_ports:
        print("사용 가능한 시리얼 포트를 찾을 수 없습니다.")
        print("다음을 확인해주세요:")
        print("1. 센서가 제대로 연결되어 있는지")
        print("2. 사용자가 dialout 그룹에 속해있는지")
        print("3. 포트 권한이 올바른지")
        sys.exit(1)
    
    print("발견된 포트들:", available_ports)
    return available_ports[0]  # 첫 번째 사용 가능한 포트 반환

# Discord 웹훅 URL 설정
WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL"  # Discord 웹훅 URL 입력

def init_serial():
    """시리얼 연결 초기화"""
    port = find_serial_port()
    print(f"연결 시도 중인 포트: {port}")
    
    try:
        ser = serial.Serial(
            port=port,
            baudrate=9600,
            timeout=1
        )
        print(f"시리얼 포트 {port} 연결 성공!")
        return ser
    except serial.SerialException as e:
        print(f"시리얼 포트 연결 실패: {str(e)}")
        sys.exit(1)

def send_discord_alert(co2_level, status):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if co2_level < 700:
        color = 0x00FF00
    elif co2_level < 1000:
        color = 0xFFFF00
    else:
        color = 0xFF0000

    data = {
        "embeds": [{
            "title": "CO2 센서 알림",
            "description": f"CO2 농도가 {status}입니다.",
            "color": color,
            "fields": [
                {
                    "name": "CO2 농도",
                    "value": f"{co2_level} ppm",
                    "inline": True
                },
                {
                    "name": "상태",
                    "value": status,
                    "inline": True
                },
                {
                    "name": "측정 시간",
                    "value": current_time,
                    "inline": False
                }
            ],
            "footer": {
                "text": "CO2 모니터링 시스템"
            }
        }]
    }

    try:
        response = requests.post(WEBHOOK_URL, json=data)
        if response.status_code == 204:
            print(f"Discord 알림 전송 성공 - CO2: {co2_level}ppm")
        else:
            print(f"Discord 알림 전송 실패: {response.status_code}")
    except Exception as e:
        print(f"Discord 알림 전송 중 오류: {str(e)}")

def read_co2(ser):
    """CO2 값 읽기"""
    command = bytearray([0x11, 0x01, 0x01, 0xED])
    ser.write(command)
    time.sleep(0.1)
    
    if ser.in_waiting >= 7:
        response = ser.read(7)
        if len(response) >= 7:
            co2 = (response[3] * 256) + response[4]
            return co2
    return -1

def get_status(co2_level):
    if co2_level < 700:
        return "좋음"
    elif co2_level < 1000:
        return "보통"
    elif co2_level < 2000:
        return "환기 필요"
    else:
        return "즉시 환기 필요!"

def main():
    ser = init_serial()
    last_alert_time = 0
    ALERT_INTERVAL = 600  # 10분
    
    print("CO2 모니터링 시작...")
    send_discord_alert(0, "모니터링 시작")
    
    while True:
        try:
            co2 = read_co2(ser)
            current_time = time.time()
            
            if co2 > 0:
                status = get_status(co2)
                print(f"CO2: {co2} ppm - 상태: {status}")
                
                if (current_time - last_alert_time) >= ALERT_INTERVAL:
                    send_discord_alert(co2, status)
                    last_alert_time = current_time
                elif co2 >= 2000 and (current_time - last_alert_time) >= 60:
                    send_discord_alert(co2, "긴급: 즉시 환기 필요!")
                    last_alert_time = current_time
                
            print("-" * 30)
            time.sleep(10)
            
        except KeyboardInterrupt:
            print("\n프로그램 종료")
            break
        except Exception as e:
            print(f"오류 발생: {str(e)}")
            time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"프로그램 실행 중 오류 발생: {str(e)}")
    finally:
        print("프로그램 종료")

```

실행 전 확인사항:

1. 시리얼 포트 권한 설정:
```bash
sudo usermod -a -G dialout $USER
sudo chmod 666 /dev/ttyACM*  # 또는 실제 포트
```

2. 필요한 패키지 설치:
```bash
pip3 install pyserial requests
```

3. 장치 연결 확인:
```bash
ls -l /dev/ttyACM*
```
또는
```bash
ls -l /dev/ttyUSB*
```

이제 다시 실행해보세요:
```bash
python3 discord_co2.py
```

문제가 지속되면 어떤 포트가 발견되었는지 알려주세요!

discord code
```
import serial
import time
import requests
import json
from datetime import datetime
import glob
import sys

def find_serial_port():
    """사용 가능한 시리얼 포트 찾기"""
    ports = glob.glob('/dev/tty[A-Za-z]*')
    available_ports = []
    
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            available_ports.append(port)
        except (OSError, serial.SerialException):
            pass
    
    if not available_ports:
        print("사용 가능한 시리얼 포트를 찾을 수 없습니다.")
        print("다음을 확인해주세요:")
        print("1. 센서가 제대로 연결되어 있는지")
        print("2. 사용자가 dialout 그룹에 속해있는지")
        print("3. 포트 권한이 올바른지")
        sys.exit(1)
    
    print("발견된 포트들:", available_ports)
    return available_ports[0]  # 첫 번째 사용 가능한 포트 반환

# Discord 웹훅 URL 설정
WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL"  # Discord 웹훅 URL 입력

def init_serial():
    """시리얼 연결 초기화"""
    port = find_serial_port()
    print(f"연결 시도 중인 포트: {port}")
    
    try:
        ser = serial.Serial(
            port=port,
            baudrate=9600,
            timeout=1
        )
        print(f"시리얼 포트 {port} 연결 성공!")
        return ser
    except serial.SerialException as e:
        print(f"시리얼 포트 연결 실패: {str(e)}")
        sys.exit(1)

def send_discord_alert(co2_level, status):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if co2_level < 700:
        color = 0x00FF00
    elif co2_level < 1000:
        color = 0xFFFF00
    else:
        color = 0xFF0000

    data = {
        "embeds": [{
            "title": "CO2 센서 알림",
            "description": f"CO2 농도가 {status}입니다.",
            "color": color,
            "fields": [
                {
                    "name": "CO2 농도",
                    "value": f"{co2_level} ppm",
                    "inline": True
                },
                {
                    "name": "상태",
                    "value": status,
                    "inline": True
                },
                {
                    "name": "측정 시간",
                    "value": current_time,
                    "inline": False
                }
            ],
            "footer": {
                "text": "CO2 모니터링 시스템"
            }
        }]
    }

    try:
        response = requests.post(WEBHOOK_URL, json=data)
        if response.status_code == 204:
            print(f"Discord 알림 전송 성공 - CO2: {co2_level}ppm")
        else:
            print(f"Discord 알림 전송 실패: {response.status_code}")
    except Exception as e:
        print(f"Discord 알림 전송 중 오류: {str(e)}")

def read_co2(ser):
    """CO2 값 읽기"""
    command = bytearray([0x11, 0x01, 0x01, 0xED])
    ser.write(command)
    time.sleep(0.1)
    
    if ser.in_waiting >= 7:
        response = ser.read(7)
        if len(response) >= 7:
            co2 = (response[3] * 256) + response[4]
            return co2
    return -1

def get_status(co2_level):
    if co2_level < 700:
        return "좋음"
    elif co2_level < 1000:
        return "보통"
    elif co2_level < 2000:
        return "환기 필요"
    else:
        return "즉시 환기 필요!"

def main():
    ser = init_serial()
    last_alert_time = 0
    ALERT_INTERVAL = 600  # 10분
    
    print("CO2 모니터링 시작...")
    send_discord_alert(0, "모니터링 시작")
    
    while True:
        try:
            co2 = read_co2(ser)
            current_time = time.time()
            
            if co2 > 0:
                status = get_status(co2)
                print(f"CO2: {co2} ppm - 상태: {status}")
                
                if (current_time - last_alert_time) >= ALERT_INTERVAL:
                    send_discord_alert(co2, status)
                    last_alert_time = current_time
                elif co2 >= 2000 and (current_time - last_alert_time) >= 60:
                    send_discord_alert(co2, "긴급: 즉시 환기 필요!")
                    last_alert_time = current_time
                
            print("-" * 30)
            time.sleep(10)
            
        except KeyboardInterrupt:
            print("\n프로그램 종료")
            break
        except Exception as e:
            print(f"오류 발생: {str(e)}")
            time.sleep(5)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"프로그램 실행 중 오류 발생: {str(e)}")
    finally:
        print("프로그램 종료")
```
<b>  Discord 웹훅 URL을 얻는 방법
1. Discord 웹훅 생성 방법:
   1. Discord 서버에서 설정(⚙️) 클릭
   2. 앱 통합 선택
   3. 웹후크 선택
   4. 새 웹후크 클릭
   5. 이름 입력 (예: "CO2 알림")
   6. 채널 선택
   7. 웹후크 URL 복사

2. 코드에서 변경할 부분:
```python
# 이 부분을
WEBHOOK_URL = "YOUR_DISCORD_WEBHOOK_URL"

# 복사한 웹훅 URL로 변경 (예시)
WEBHOOK_URL = "https://discord.com/api/webhooks/123456789/abcdefghijklmnopqrstuvwxyz"
```

웹훅 URL은 대략 이런 형태입니다:
`https://discord.com/api/webhooks/[ID]/[TOKEN]`

웹훅을 생성하고 URL을 알려주시면, 제가 코드에 적용하는 것을 도와드리겠습니다!



=================    제슨나노와 이산화탄소 센서     uart tx, rx ========================================

![image](https://github.com/user-attachments/assets/07045f93-aa14-474d-ab94-5c5c1ca9a345)

CM1106 센서를 Jetson Nano에 연결하는 방법을 설명해드리겠습니다:

1. 연결 핀 매핑:
- CM1106의 TX → Jetson Nano의 RX (UART RXD, GPIO PIN)
- CM1106의 RX → Jetson Nano의 TX (UART TXD, GPIO PIN)
- CM1106의 5V → Jetson Nano의 5V 전원
- CM1106의 GND → Jetson Nano의 GND

2. Jetson Nano에서 UART 포트 활성화:
```bash
sudo systemctl stop nvgetty
sudo systemctl disable nvgetty
```

3. UART 권한 설정:
```bash
sudo usermod -a -G dialout $USER
```
4, 설치.
```
sudo apt-get update
sudo apt-get install python3-pip
sudo apt-get install python3-serial
```
5, Python 패키지 설치:
```
pip3 install pyserial
pip3 install numpy  # 데이터 처리용
```
6. CM1106 전용 파이썬 코드 예시::
   
```python
import serial
import time

class CM1106:
    def __init__(self, port='/dev/ttyTHS1', baudrate=9600):
        self.serial = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=2
        )
        
    def read_co2(self):
        # CM1106 명령어 형식: 0x11 0x01 0x01 0xED
        cmd = b'\x11\x01\x01\xED'
        self.serial.write(cmd)
        time.sleep(0.1)
        
        if self.serial.in_waiting:
            response = self.serial.read(8)  # 8바이트 응답
            if len(response) == 8:
                co2 = (response[3] << 8) + response[4]
                return co2
        return None

    def close(self):
        self.serial.close()

# 사용 예시
if __name__ == "__main__":
    sensor = CM1106()
    try:
        while True:
            co2_value = sensor.read_co2()
            if co2_value is not None:
                print(f"CO2 concentration: {co2_value} ppm")
            time.sleep(2)
    except KeyboardInterrupt:
        sensor.close()
```

<b> error
이 에러는 '/dev/ttyTHS1' 포트에 대한 접근 권한이 없어서 발생하는 문제입니다. 다음 단계들을 순서대로 실행하여 해결할 수 있습니다:

1. 먼저 사용자를 dialout 그룹에 추가:
```bash
sudo usermod -a -G dialout $USER
sudo usermod -a -G tty $USER
```

2. UART 포트의 권한 변경:
```bash
sudo chmod 666 /dev/ttyTHS1
```

3. nvgetty 서비스 중지 및 비활성화:
```bash
sudo systemctl stop nvgetty
sudo systemctl disable nvgetty
```
<b>  4번처럼 하는 이유. 
nvgetty 관련 명령어들의 의미를 설명해드리겠습니다:

`sudo systemctl stop nvgetty`와 `sudo systemctl disable nvgetty`는 Jetson Nano의 시리얼 통신과 관련된 중요한 설정입니다.

1. `nvgetty`란?
- NVIDIA Jetson의 시리얼 콘솔 서비스입니다
- 기본적으로 UART 포트를 시리얼 콘솔용으로 사용하도록 설정되어 있습니다
- 이 서비스가 실행 중이면 우리가 센서와 통신하려는 UART 포트를 독점하게 됩니다

2. 각 명령어의 의미:
- `sudo systemctl stop nvgetty`: 현재 실행 중인 nvgetty 서비스를 중지합니다
- `sudo systemctl disable nvgetty`: 시스템 부팅 시 nvgetty 서비스가 자동으로 시작되지 않도록 비활성화합니다

3. 왜 이 설정이 필요한가요?
- CM1106 센서가 사용하려는 UART 포트를 nvgetty 서비스가 사용 중이면 충돌이 발생합니다
- 센서와 정상적인 통신을 위해서는 이 서비스를 중지하고 비활성화해야 합니다
- 이렇게 하면 UART 포트를 센서 통신용으로 전용으로 사용할 수 있습니다

이 설정을 하지 않으면 센서와의 통신이 실패하거나 에러가 발생할 수 있습니다.


4. 변경사항 적용을 위해 시스템 재부팅:
```bash
sudo reboot
```

5. 재부팅 후 포트 권한 확인:
```bash
ls -l /dev/ttyTHS1
```


```bash
sudo python3 co2_jetson_only.py
```


