#include "mqtt_client.h"
#include <WiFi.h>
#include <PubSubClient.h>
#include "secrets.h"  // Using secrets file for credentials

WiFiClient espClient;
PubSubClient client(espClient);

void setupWiFi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(WIFI_SSID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected.");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
}

void initMQTT() {
  setupWiFi();
  client.setServer(MQTT_SERVER, MQTT_PORT);
  while (!client.connected()) {
    Serial.print("Connecting to MQTT broker...");
    if (client.connect("ESP32Client")) {
      Serial.println("connected.");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" - try again in 5 seconds.");
      delay(5000);
    }
  }
}

void publishData(const String &payload) {
  if (!client.connected()) {
    Serial.println("MQTT disconnected. Reconnecting...");
    initMQTT();
  }
  client.loop();
  Serial.print("Publishing payload: ");
  Serial.println(payload);
  client.publish(MQTT_TOPIC, payload.c_str());
}