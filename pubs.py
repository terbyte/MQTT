import paho.mqtt.client as mqtt
import json
client = mqtt.Client()
import time
from datetime import datetime, timedelta
client.connect("192.168.0.101", 1883)
# client.connect("10.11.12.50", 1883)
timenow=datetime.now()
timenow=timenow.strftime('%Y-%m-%d %H:%M:%S')	
d1=datetime.strptime(timenow,'%Y-%m-%d %H:%M:%S')

def publisher(cardcodes):

    jsonfileS ={"tblname": "timeindb",
            "data": {
              "cardcode": cardcodes,
              "vehicle": 'KALESA',
              "plate": 'string',
              "timein": timenow,#date format string
              "operator":'string',
              "pic":'string',
              "pic2":'string',
              "lane":'string',
              "pc":'string',
              "exit_log_id":12, #ask what is this column for
        }
    }

    # print(jsonfileS)
    data_out= json.dumps(jsonfileS)
    # print(data_out)
    # client.publish("pms/entry/pmsdis002/dbdata", data_out)


      # client.publish("pms/entry/pmsdis002/dbdata", input("Message:"))
    client.publish("pms/entry/pmsdis002/dbdata", data_out)
