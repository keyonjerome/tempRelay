#include <SPI.h>
#include <LoRa.h>  

 
#define ss 5
#define rst 14
#define dio0 2
String inString = "";    // string to hold incoming charaters
String MyMessage = ""; // Holds the complete message
 
void setup() {
  Serial.begin(115200);
  while (!Serial);
  Serial.println("LoRa Receiver");
  LoRa.setPins(ss,rst,dio0);
  while(!LoRa.begin(433E6)) { // or 915E6
    Serial.println("Starting LoRa failed!");
    delay(5000);
  }
}
 
void loop() {
  
  // try to parse packet
  int packetSize = LoRa.parsePacket();
  if (packetSize) { 
    // read packet    
    while (LoRa.available())
    {
      int inChar = LoRa.read();
      inString += (char)inChar;
      MyMessage = inString;       
    }
    inString = "";     
    LoRa.packetRssi();    
  }
      
  Serial.println(MyMessage);  
  
}
