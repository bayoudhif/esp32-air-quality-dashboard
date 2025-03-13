#ifndef SENSORS_H
#define SENSORS_H

#include <Arduino.h>

// Structure to hold sensor data
struct SensorData {
  float temperature;
  float humidity;
  int mq135Value;
  uint16_t eco2;
  uint16_t tvoc;
  float pm25;
  float pm10;
};

// Function prototypes for sensor initialization and reading
void initSensors();
SensorData readSensors();
String generatePayload(const SensorData &data);

#endif
