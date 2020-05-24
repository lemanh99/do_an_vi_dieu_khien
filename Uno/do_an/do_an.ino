//Thêm thư viện LiquitCrystal - nó có sẵn vì vậy bạn không cần cài thêm gì cả
#include <LiquidCrystal.h>
#include <OneWire.h>
#include <DallasTemperature.h>
#include <SoftwareSerial.h>
#include <ArduinoJson.h>
#include <SerialCommand.h>
//Khởi tạo với các chân

#define ONE_WIRE_BUS 8
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);
float Celsius = 0;
int sensor = A0;

const byte RX = 3;  
const byte TX = 2;    
SoftwareSerial mySerial(RX, TX); 
SerialCommand sCmd(mySerial);

void setup() {
  Serial.begin(57600);
  mySerial.begin(57600);
  //sensors.begin();
  //pinMode(sensor, INPUT);
  sCmd.addCommand("Flow", flow);
  sCmd.addCommand("send", relay);
  Serial.println("Da san sang nhan lenh");
  pinMode(7, OUTPUT);
  digitalWrite(7, HIGH);
}
 
void loop() {
    sCmd.readSerial();
}

void flow() {
    Serial.println("Flow");
    int j = analogRead(sensor); 
    j=map(j,0,1023,100,0);
    Serial.println(j);
    sensors.requestTemperatures();
    Celsius = sensors.getTempCByIndex(0);
    Serial.println(Celsius);
    StaticJsonBuffer<200> jsonBuffer2;
    JsonObject& root2 = jsonBuffer2.createObject();
    String command = "FArdunio";
    root2["Temp"] = Celsius;
    root2["Humi"] = j;
    mySerial.print(command);
    mySerial.print('\r');
    root2.printTo(mySerial);
    mySerial.print('\r');
}
void relay(){
  Serial.print("relay");
  char *json = sCmd.next();
  StaticJsonBuffer<200> jsonBuffer2;
  JsonObject& root = jsonBuffer2.parseObject(json);
  int t = root["val"];
  Serial.print(t);
  digitalWrite(7, LOW);
  delay(3000);
  digitalWrite(7, HIGH);
}
