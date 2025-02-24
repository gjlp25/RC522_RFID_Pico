import utime
import network
import secrets
from simple import MQTTClient, MQTTException

# Connect to WiFi
def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    while not wlan.isconnected():
        utime.sleep(1)
    print('Connected to WiFi')
    ip_address = wlan.ifconfig()[0]
    print(f'IP Address: {ip_address}')
    print('Network configuration:', wlan.ifconfig())

# MQTT Configuration
mqtt_server = secrets.mqtt_server
mqtt_port = secrets.mqtt_port
mqtt_client_id = secrets.mqtt_client_id
mqtt_user = secrets.mqtt_user
mqtt_password = secrets.mqtt_password

# Connect to WiFi
connect_to_wifi(secrets.wifi_ssid, secrets.wifi_password)

# Test MQTT connection
def test_mqtt_connection():
    try:
        client = MQTTClient(mqtt_client_id, mqtt_server, port=mqtt_port, user=mqtt_user, password=mqtt_password)
        print(f"Connecting to MQTT server {mqtt_server}:{mqtt_port} with client ID {mqtt_client_id}")
        client.connect()
        print("MQTT connection successful")
        client.disconnect()
    except MQTTException as e:
        print(f"Failed to connect to MQTT server: {e}")
        if e.args[0] == 5:
            print("Connection refused: not authorized. Please check your MQTT credentials.")

# Run the test
test_mqtt_connection()
