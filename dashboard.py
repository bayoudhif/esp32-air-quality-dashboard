import json
import time
import threading
import os
from collections import deque

import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
import paho.mqtt.client as mqtt
from dotenv import load_dotenv
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# Load environment variables from .env file
load_dotenv()

# MQTT configuration from .env
MQTT_BROKER = os.getenv("MQTT_BROKER", "broker.hivemq.com")
MQTT_PORT = int(os.getenv("MQTT_PORT", "1883"))
MQTT_TOPIC = os.getenv("MQTT_TOPIC", "your/topic")

# InfluxDB configuration from .env
INFLUXDB_URL = os.getenv("INFLUXDB_URL", "http://localhost:8086")
INFLUXDB_TOKEN = os.getenv("INFLUXDB_TOKEN", "YOUR_INFLUXDB_TOKEN")
INFLUXDB_ORG = os.getenv("INFLUXDB_ORG", "YOUR_ORG")
INFLUXDB_BUCKET = os.getenv("INFLUXDB_BUCKET", "sensor_data")

# Initialize InfluxDB client
influx_client = InfluxDBClient(url=INFLUXDB_URL, token=INFLUXDB_TOKEN, org=INFLUXDB_ORG)
write_api = influx_client.write_api(write_options=SYNCHRONOUS)

# Global variables to store sensor data (limit to the last 50 readings)
MAX_DATA_POINTS = 50
sensor_data = {
    'time': deque(maxlen=MAX_DATA_POINTS),
    'temperature': deque(maxlen=MAX_DATA_POINTS),
    'humidity': deque(maxlen=MAX_DATA_POINTS),
    'mq135': deque(maxlen=MAX_DATA_POINTS),
    'eco2': deque(maxlen=MAX_DATA_POINTS),
    'tvoc': deque(maxlen=MAX_DATA_POINTS),
    'pm25': deque(maxlen=MAX_DATA_POINTS),
    'pm10': deque(maxlen=MAX_DATA_POINTS)
}

def write_sensor_data(record):
    """
    Write sensor data to InfluxDB.
    `record` is a dictionary containing sensor values and a timestamp.
    """
    try:
        point = Point("air_quality") \
            .tag("location", "home") \
            .field("temperature", record["temperature"] if record["temperature"] is not None else 0) \
            .field("humidity", record["humidity"] if record["humidity"] is not None else 0) \
            .field("mq135", record["mq135"] if record["mq135"] is not None else 0) \
            .field("eco2", record["eco2"] if record["eco2"] is not None else 0) \
            .field("tvoc", record["tvoc"] if record["tvoc"] is not None else 0) \
            .field("pm25", record["pm25"] if record["pm25"] is not None else 0) \
            .field("pm10", record["pm10"] if record["pm10"] is not None else 0) \
            .time(record["time"], WritePrecision.S)
        write_api.write(bucket=INFLUXDB_BUCKET, record=point)
        print("Data written to InfluxDB.")
    except Exception as e:
        print("Failed to write to InfluxDB:", e)

# MQTT Callbacks
def on_connect(client, userdata, flags, rc):
    print("Connected to MQTT broker with result code " + str(rc))
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode("utf-8")
        data = json.loads(payload)
        timestamp = int(time.time())  # Unix timestamp in seconds

        # Append data to in-memory storage
        sensor_data['time'].append(timestamp)
        sensor_data['temperature'].append(data.get('temperature'))
        sensor_data['humidity'].append(data.get('humidity'))
        sensor_data['mq135'].append(data.get('mq135'))
        sensor_data['eco2'].append(data.get('eco2'))
        sensor_data['tvoc'].append(data.get('tvoc'))
        sensor_data['pm25'].append(data.get('pm25'))
        sensor_data['pm10'].append(data.get('pm10'))

        # Prepare record for InfluxDB
        sensor_record = {
            "time": timestamp,
            "temperature": data.get('temperature'),
            "humidity": data.get('humidity'),
            "mq135": data.get('mq135'),
            "eco2": data.get('eco2'),
            "tvoc": data.get('tvoc'),
            "pm25": data.get('pm25'),
            "pm10": data.get('pm10')
        }
        write_sensor_data(sensor_record)
    except Exception as e:
        print("Error processing MQTT message:", e)

def mqtt_thread():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()
    except Exception as e:
        print("Error connecting to MQTT broker:", e)

# Start the MQTT client in a separate thread so your dashboard can run simultaneously
threading.Thread(target=mqtt_thread, daemon=True).start()

# Set up the Dash app
app = dash.Dash(__name__)
app.layout = html.Div([
    html.H1("Air Quality Dashboard"),
    dcc.Interval(id='interval-component', interval=5*1000, n_intervals=0),
    dcc.Graph(id='temp-humidity-graph'),
    dcc.Graph(id='gas-graph'),
    dcc.Graph(id='pm-graph')
])

@app.callback(
    [Output('temp-humidity-graph', 'figure'),
     Output('gas-graph', 'figure'),
     Output('pm-graph', 'figure')],
    [Input('interval-component', 'n_intervals')]
)
def update_graphs(n):
    time_data = list(sensor_data['time'])
    
    # Temperature & Humidity Graph
    temp_trace = go.Scatter(
        x=time_data, y=list(sensor_data['temperature']),
        mode='lines+markers', name='Temperature (°C)'
    )
    hum_trace = go.Scatter(
        x=time_data, y=list(sensor_data['humidity']),
        mode='lines+markers', name='Humidity (%)'
    )
    temp_hum_layout = go.Layout(
        title='Temperature & Humidity', xaxis=dict(title='Time'), yaxis=dict(title='Value')
    )
    temp_hum_fig = go.Figure(data=[temp_trace, hum_trace], layout=temp_hum_layout)
    
    # Gas Sensor Graph (eCO2 and TVOC)
    eco2_trace = go.Scatter(
        x=time_data, y=list(sensor_data['eco2']),
        mode='lines+markers', name='eCO2 (ppm)'
    )
    tvoc_trace = go.Scatter(
        x=time_data, y=list(sensor_data['tvoc']),
        mode='lines+markers', name='TVOC (ppb)'
    )
    gas_layout = go.Layout(
        title='Gas Sensor Readings', xaxis=dict(title='Time'), yaxis=dict(title='Value')
    )
    gas_fig = go.Figure(data=[eco2_trace, tvoc_trace], layout=gas_layout)
    
    # Particulate Matter Graph (PM2.5 and PM10)
    pm25_trace = go.Scatter(
        x=time_data, y=list(sensor_data['pm25']),
        mode='lines+markers', name='PM2.5 (µg/m³)'
    )
    pm10_trace = go.Scatter(
        x=time_data, y=list(sensor_data['pm10']),
        mode='lines+markers', name='PM10 (µg/m³)'
    )
    pm_layout = go.Layout(
        title='Particulate Matter Readings', xaxis=dict(title='Time'), yaxis=dict(title='Value')
    )
    pm_fig = go.Figure(data=[pm25_trace, pm10_trace], layout=pm_layout)
    
    return temp_hum_fig, gas_fig, pm_fig

if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0')
