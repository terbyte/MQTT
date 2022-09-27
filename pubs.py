import paho.mqtt.client as mqtt

client = mqtt.Client()
client.connect('localhost', 9999)

while True:
    client.publish("Gerome/test", input('Message : '))