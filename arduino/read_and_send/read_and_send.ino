
  
#include "DHT.h"
#include <LoRa.h>
#include <SPI.h>
 
// Definit la broche de l'Arduino sur laquelle la 
// broche DATA du capteur est reliee 
#define DHTPIN 13
  
// Definit le type de capteur utilise
#define DHTTYPE DHT11
  
// Declare un objet de type DHT
// Il faut passer en parametre du constructeur 
// de l'objet la broche et le type de capteur
DHT dht(DHTPIN, DHTTYPE);
  
#define ss 5
#define rst 14
#define dio0 2
#define delay_wait 500
 
uint32_t seqNum = 0;
typedef struct {
  uint32_t sequenceNum = 1;
  float temperature = -45;
  float humidity = -1;
  float heatIndex = -1;
} Temp_Data;

Temp_Data tData;
void setup() 
{

  Serial.begin(115200);
  while (!Serial);
  Serial.println("LoRa transceiver");
  dht.begin();
  LoRa.setPins(ss, rst, dio0);    //setup LoRa transceiver module
  
  while (!LoRa.begin(433E6))     //433E6 - Asia, 866E6 - Europe, 915E6 - North America
  {
    delay(delay_wait);
    Serial.println("LoRa start failed");
  }
//  LoRa.setSyncWord(0xA5);
  Serial.println("Leaving setup");
}
 
void loop() 
{
  Serial.println("Starting new packet");
  tData.sequenceNum = seqNum;
  tData.temperature = dht.readTemperature();
  tData.humidity = dht.readHumidity();
  tData.heatIndex = dht.computeHeatIndex(tData.temperature,tData.humidity,true);
  

  
  LoRa.beginPacket();   //Send LoRa packet to receiver
  LoRa.write((const uint8_t*)&tData,sizeof(tData));
  LoRa.endPacket();

  Serial.print(tData.sequenceNum);
  Serial.print(" ");
  Serial.print(tData.temperature);
  Serial.print(" ");
  Serial.print(tData.humidity);    
  Serial.print(" ");
  Serial.print(tData.heatIndex);
  Serial.print("\n");
  Serial.println("Sent packet");
  seqNum++;
  delay(delay_wait);
}
