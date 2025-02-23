
# 아두이노 이산화탄소 보정 프로그램.  원래 시리얼 프로그램이 부정확해서 보정함.
#include <SoftwareSerial.h>
 
SoftwareSerial mySerial(13, 11);
unsigned char Send_data[4] = {0x11,0x01,0x01,0xED};
unsigned char Receive_Buff[8];
unsigned char recv_cnt = 0;
unsigned int PPM_Value;

void Send_CMD(void) {
  for(int i=0; i<4; i++) {
    mySerial.write(Send_data[i]);
    delay(1);
  }
}

unsigned char Checksum_cal(void) {
  unsigned char SUM=0;
  for(unsigned char count=0; count<7; count++) {
    SUM += Receive_Buff[count];
  }
  return 256-SUM;
}
 
void setup() {
  pinMode(13,INPUT);
  pinMode(11,OUTPUT);
  Serial.begin(9600);
  Serial.println("Starting CO2 measurements...");
  while (!Serial);
  mySerial.begin(9600);
  while (!mySerial);
}
 
void loop() {
  Send_CMD();
 
  while(1) {
    if(mySerial.available()) { 
      Receive_Buff[recv_cnt++] = mySerial.read();
      if(recv_cnt == 8) {
        recv_cnt = 0;
        break;
      }
    }
  } 
  
  if(Checksum_cal() == Receive_Buff[7]) {
    PPM_Value = Receive_Buff[3]<<8 | Receive_Buff[4];
    
    // CO2 보정
    float calibration_factor = 0.2;  // 보정 계수
    float base_co2 = 400.0;          // 기본 CO2 농도
    PPM_Value = (PPM_Value * calibration_factor) + base_co2;
    
    Serial.print("CO2: ");
    Serial.print(PPM_Value);
    Serial.println(" ppm");
  } else {
    Serial.println("Checksum Error");
  }
  
  delay(1000);  // 1초 딜레이
}
