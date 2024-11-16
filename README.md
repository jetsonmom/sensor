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


