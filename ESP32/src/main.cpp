#include <Arduino.h>
#include "sensors.h"
#include "mqtt_client.h"

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("Project starting...");

  // Initialize sensors and MQTT client
  initSensors();
  initMQTT();
}

void loop() {
  // Read sensor data
  SensorData data = readSensors();
  // Convert sensor data to a JSON formatted string
  String payload = generatePayload(data);

  // Publish data via MQTT
  publishData(payload);

  // Delay between readings
  delay(5000);
}
