from machine import Pin
from mfrc522 import MFRC522
import utime
import network
import secrets
from simple import MQTTClient, MQTTException

# Dictionary for authorized cards with names
AUTHORIZED_CARDS = {
    1036396588: "Wies",
    571511444: "Tim"
}

# Initialize the RFID reader with specified SPI pins
reader = MFRC522(spi_id=0, sck=Pin(6, Pin.OUT), miso=Pin(4, Pin.OUT), mosi=Pin(7, Pin.OUT), cs=Pin(5, Pin.OUT), rst=Pin(22, Pin.OUT))

# Initialize the GPIO pins for the LEDs and the buzzer
led_pins = {
    "red": Pin(13, Pin.OUT),
    "green": Pin(12, Pin.OUT)
}
beep = Pin(10, Pin.OUT)

# MQTT Configuration
mqtt_config = {
    "server": secrets.mqtt_server,
    "port": secrets.mqtt_port,
    "topic": secrets.mqtt_topic,
    "client_id": secrets.mqtt_client_id,
    "user": secrets.mqtt_user,
    "password": secrets.mqtt_password
}

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

connect_to_wifi(secrets.wifi_ssid, secrets.wifi_password)

# Send MQTT message
def send_mqtt_message(topic, message):
    try:
        client = MQTTClient(mqtt_config["client_id"], mqtt_config["server"], port=mqtt_config["port"], user=mqtt_config["user"], password=mqtt_config["password"])
        print(f"Connecting to MQTT server {mqtt_config['server']}:{mqtt_config['port']} with client ID {mqtt_config['client_id']}")
        client.connect()
        print(f"Publishing message to topic {topic}")
        client.publish(topic, message)
        client.disconnect()
        print("MQTT message sent successfully")
    except MQTTException as e:
        print(f"Failed to send MQTT message: {e}")
        if e.args[0] == 5:
            print("Connection refused: not authorized. Please check your MQTT credentials.")

print("Bring RFID TAG Closer...\n")

def reset_leds():
    for led in led_pins.values():
        led.value(0)

def beep_buzzer(times, delay):
    for _ in range(times):
        beep.value(1)
        utime.sleep(delay)
        beep.value(0)
        utime.sleep(delay)

def handle_card(card_id, authorized):
    if authorized:
        name = AUTHORIZED_CARDS[card_id]
        print(f"Card ID: {card_id} (Name: {name}) PASS: Green Light Activated")
        led_color = "green"
        beep_times = 1
        beep_delay = 0.5
        mqtt_message = f"Authorized card {name} scanned"
    else:
        print(f"Card ID: {card_id} UNKNOWN CARD! Red Light Activated")
        led_color = "red"
        beep_times = 3
        beep_delay = 0.1
        mqtt_message = f"Unauthorized card {card_id} scanned"
    
    reset_leds()
    led_pins[led_color].value(1)
    beep_buzzer(beep_times, beep_delay)
    led_pins[led_color].value(0)
    send_mqtt_message(f"rc522/card/{'authorized' if authorized else 'unauthorized'}", mqtt_message)

while True:
    reader.init()
    stat, tag_type = reader.request(reader.REQIDL)
    if stat == reader.OK:
        stat, uid = reader.SelectTagSN()
        if stat == reader.OK:
            card_id = int.from_bytes(bytes(uid), "little", False)
            handle_card(card_id, card_id in AUTHORIZED_CARDS)
    utime.sleep_ms(100)