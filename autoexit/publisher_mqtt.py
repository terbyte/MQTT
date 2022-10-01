import paho.mqtt.client as mqtt 


def send_mqttLogs(ip,topic,message):
	try:
		mqttBroker =ip
		client = mqtt.Client("DISPENSER")
		client.connect(mqttBroker)
		mymessage = message
		client.publish(topic, mymessage)
		print(f"Just published {mymessage} to topic {topic}")
		return 1		
	except:
		return 0

