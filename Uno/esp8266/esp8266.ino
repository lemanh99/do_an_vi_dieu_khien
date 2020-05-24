#include <ESP8266WiFi.h>
#include <SocketIOClient.h>
#include <SoftwareSerial.h>
#include <SerialCommand.h>

const byte RX = D1;
const byte TX = D2;

SoftwareSerial mySerial(RX, TX);
SerialCommand sCmd(mySerial);

SocketIOClient socket;
//const char* ssid = "Minh";
//const char* password = "100419999"; 
const char* ssid = "Dung Leo Nheo";
const char* password = "khongchomo"; 

//char host[] = "172.20.10.11"; 
char host[] = "192.168.1.226"; 
int port = 3484;  

char namespace_esp8266[] = "esp8266";

extern String RID;
extern String Rfull;

unsigned long previousMillis = 0;
long interval = 2000;

void setup() {
  Serial.begin(57600);
  mySerial.begin(57600);
  delay(10);

  Serial.print("Ket noi vao mang: ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print('.');
  }
  
  Serial.println();
  Serial.println(F("Da ket noi WiFi"));
  Serial.println(F("Dia chi IP cua ESP8266 (Socket Client ESP8266): "));
  Serial.println(WiFi.localIP());
  
  if (!socket.connect(host, port, namespace_esp8266)) {
    Serial.println(F("Ket noi den socket server that bai!"));
    return;
  }
  
  if (socket.connected()) {
    Serial.println(F("Ket noi den socket server thanh cong!"));
    socket.send("connection2", "message", "da ket noi!!!");
 }

  Serial.println("Da san sang nhan lenh");
  sCmd.addDefaultHandler(defaultCommand);
  
}

void loop (){
  sCmd.readSerial(); 
  if (socket.monitor()) {
    Serial.println(RID);
    Serial.println(Rfull);
    
    mySerial.print(RID);
    mySerial.print('\r');
    mySerial.print(Rfull);
    mySerial.print('\r');
  }
  //ket noi lai
  if (!socket.connected()) {
    socket.reconnect(host, port, namespace_esp8266);
  }
}

void defaultCommand(String command){
  char *json = sCmd.next();
  if (command == "FArdunio")
  socket.send(command, json);
}
