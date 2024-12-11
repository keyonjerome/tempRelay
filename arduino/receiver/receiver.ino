#include <SPI.h>
#include <LoRa.h>  

 
#define ss 5
#define rst 14
#define dio0 2
String inString = "";    // string to hold incoming charaters
String MyMessage = ""; // Holds the complete message

typedef struct {
  uint32_t sequenceNum = 1;
  float temperature = -45;
  float humidity = -1;
  float heatIndex = -1;
} Temp_Data;

Temp_Data tData;

 
void setup() {
  Serial.begin(115200);
  while (!Serial);
  Serial.println("LoRa Receiver0");
  LoRa.setPins(ss,rst,dio0);
  Serial.println("Set pins successfully!");
  while(!LoRa.begin(433E6)) { // or 915E6
    Serial.println("Starting LoRa failed!");
    delay(5000);
  }
  Serial.println("Leaving setup");
}
 
void loop() {
  
  // try to parse packet
  int packetSize = LoRa.parsePacket();
  if (packetSize) { 
    // read packet    
    while (LoRa.available())
    {
      LoRa.readBytes((uint8_t *)&tData, sizeof(tData));
    }     
    Serial.print(tData.sequenceNum);
    Serial.print(" ");
    Serial.print(tData.temperature);
    Serial.print(" ");
    Serial.print(tData.humidity);    
    Serial.print(" ");
    Serial.print(tData.heatIndex);
    Serial.print(" ");
    Serial.print(LoRa.packetRssi());
    Serial.print("\n");    
  }
      
  
}
