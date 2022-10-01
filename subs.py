import paho.mqtt.client as mqtt
import json
client = mqtt.Client()
client.connect("192.168.0.101", 1883)
# client.connect("10.11.12.50", 1883)
def on_connect(client, userdata, flags, rc):
    print("Connected to a broker!")
    client.subscribe("pms/entry/pmsdis002/dbdata")
    
def on_message(client, userdata, message):
    # print(message.payload.decode())
    payload = json.loads((message.payload).decode("utf-8"))
    print(payload)
while True:
    client.on_connect = on_connect
    client.on_message = on_message
    client.loop_forever()