#include "sensors.h"
#include <DHT.h>
#include <Adafruit_CCS811.h>
#include <Arduino.h>

// ---------- DHT22 Setup ----------
#define DHTPIN 4
#define DHTTYPE DHT22
DHT dht(DHTPIN, DHTTYPE);

// ---------- MQ-135 Setup ----------
#define MQ135_PIN 34

// ---------- PMS5003 Setup ----------
HardwareSerial PMSSerial(2);   
const int PMS_RX_PIN = 16;    
const int PMS_TX_PIN = 17;

// ---------- CCS811 Setup ----------
Adafruit_CCS811 ccs;

void initSensors() {
  // Initialize DHT22 sensor
  dht.begin();

  // Initialize PMS5003 sensor
  PMSSerial.begin(9600, SERIAL_8N1, PMS_RX_PIN, PMS_TX_PIN);

  // Initialize CCS811 sensor
  if (!ccs.begin()) {
    Serial.println("Failed to initialize CCS811.");
    while (true) {
      delay(1000); // Halt the program indefinitely
    }
  }

  Serial.println("Sensors initialized.");
}

SensorData readSensors() {
  SensorData data;

  // Read DHT22 sensor values
  data.temperature = dht.readTemperature();
  data.humidity = dht.readHumidity();

  if (isnan(data.temperature) || isnan(data.humidity)) {
  }
  if (isnan(data.temperature) || isnan(data.humidity)) {
    Serial.println("DHT22 reading failed. Check your wiring.");
  }

  // ---------- Read MQ-135 ----------
  data.mq135Value = analogRead(MQ135_PIN);

  // ---------- Read CCS811 ----------
  if (ccs.available()) {
    if (!ccs.readData()) {
      data.eco2 = ccs.geteCO2();
      data.tvoc = ccs.getTVOC();
    } else {
      Serial.println("Error reading CCS811.");
      data.eco2 = 0;
      data.tvoc = 0;
    }
  } else {
    Serial.println("CCS811 data not available.");
    data.eco2 = 0;
    data.tvoc = 0;
  }

  // ---------- Read PMS5003 ----------
  // Read PMS5003 sensor data
  uint8_t buffer[32];
  if (PMSSerial.available()) {
    PMSSerial.readBytes(buffer, 32);

    if (buffer[0] == 0x42 && buffer[1] == 0x4d) { 
      data.pm25 = (buffer[12] << 8) + buffer[13]; 
      data.pm10 = (buffer[14] << 8) + buffer[15]; 
    } else {
      Serial.println("Error reading PMS5003.");
      data.pm25 = 0;
      data.pm25 = 0;
      data.pm10 = 0;
    }
  } else {
    Serial.println("Error reading PMS5003.");
    data.pm25 = 0;
    data.pm10 = 0;
  }
    String payload = "{";
    payload += "\"temperature\":" + String(data.temperature, 1) + ",";
    payload += "\"humidity\":" + String(data.humidity, 1) + ",";
// This function generates a JSON formatted string for MQTT payload
// The JSON format is as follows:
// {
//   "temperature": <temperature_value>,
//   "humidity": <humidity_value>,
//   "mq135": <mq135_value>,
//   "eco2": <eco2_value>,
//   "tvoc": <tvoc_value>,
//   "pm25": <pm25_value>,
//   "pm10": <pm10_value>
// }
String generatePayload(const SensorData &data) {
  String payload = "{";
  payload += "\"temperature\":" + String(data.temperature, 1) + ",";
  payload += "\"humidity\":" + String(data.humidity, 1) + ",";
  payload += "\"mq135\":" + String(data.mq135Value) + ",";
  payload += "\"eco2\":" + String(data.eco2) + ",";
  payload += "\"tvoc\":" + String(data.tvoc) + ",";
  payload += "\"pm25\":" + String(data.pm25, 1) + ",";
  payload += "\"pm10\":" + String(data.pm10, 1);
  payload += "}";
  return payload;
}
