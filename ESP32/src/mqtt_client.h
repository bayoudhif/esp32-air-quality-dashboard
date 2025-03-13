#ifndef MQTT_CLIENT_H
#define MQTT_CLIENT_H

#include <Arduino.h>

void initMQTT();
void publishData(const String &payload);

#endif