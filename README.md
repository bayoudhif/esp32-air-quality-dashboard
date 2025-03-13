# ESP32 Air Quality Dashboard

Welcome to the **ESP32 Air Quality Dashboard**—an IoT project that monitors air quality in real time using an ESP32, multiple sensors, MQTT, InfluxDB, and a dashboard.

## Features

- **Sensor Integration:**  
  Uses PMS5003, MQ-135, CCS811, and DHT22 to measure particulate matter, gases, temperature, and humidity.
- **MQTT Communication:**  
  Pushes sensor data to an MQTT broker for seamless data transfer.
- **Data Persistence:**  
  Stores historical data in InfluxDB so you can track trends over time.
- **Real-Time Dashboard:**  
  A Dash web app displays interactive plots of your sensor data.
- **Secure Credentials:**  
  Uses a `.env` file to keep your sensitive info hidden.
## Getting Started

1. **ESP32 Setup:**
   - Wire up your sensors.
   - Install the necessary libraries (DHT, Adafruit_CCS811, PubSubClient) via the Arduino Library Manager or PlatformIO.
   - Flash the firmware to your ESP32 using your preferred IDE.

2. **Dashboard Setup:**
   - Install Python dependencies:
     ```bash
     pip install dash plotly paho-mqtt influxdb-client python-dotenv
     ```
   - Update the `.env` and `ESP32/src/secrets.h` files with your MQTT and InfluxDB credentials.
   - Run the dashboard:
     ```bash
     python dashboard.py
     ```

## Usage

Once your ESP32 is sending out data and your dashboard is live, you'll see real-time visualizations of temperature, humidity, gas readings, and particulate matter.
