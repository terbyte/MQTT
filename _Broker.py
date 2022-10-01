from datetime import datetime
import logging
import asyncio
from hbmqtt.broker import Broker
from hbmqtt.client import MQTTClient, ClientException
from hbmqtt.mqtt.constants import QOS_1
import pymysql
import pymysql.cursors
import MySQLdb.cursors
import json
import paho.mqtt.client as mqtt
logger = logging.getLogger(__name__)
DB_HOST = "192.168.0.101"
DB_USER = "mqttlogger"
DB_PASS = "1sa[mqttLogger]"
DB_NAME = "pmsdb"

config = {
    'listeners': {
        'default': {
            'type': 'tcp',
            'bind': '192.168.0.101:1883'    # 0.0.0.0:1883
        }
    },
    'sys_interval': 10,
    'topic-check': {
        'enabled': False
    },
    'plugins': ['auth_anonymous'],
        'topic-check': {
            'enabled': True,
            'plugins': ['topic_taboo'],
        }
    
}

broker = Broker(config)

@asyncio.coroutine
def startBroker():
    yield from broker.start()




def on_message(client, userdata, message):
    # print(message.payload.decode())
    payload = json.loads((message.payload).decode("utf-8"))

    print("THIS IS TYPE OF PAYLOAD; ",type(payload))
    payload_to_db(payload)

@asyncio.coroutine
def brokerGetMessage():
    C = MQTTClient()
    yield from C.connect('mqtt://192.168.0.101:1883/')
    yield from C.subscribe([
        ("pms/entry/pmsdis002/dbdata", QOS_1)
    ])
    logger.info('Subscribed!')
    try:
        for i in range(1,100):
            message = yield from C.deliver_message()
            packet = message.publish_packet
            print("\nPACKET : ",packet)
            val = (str(packet.payload.data.decode('utf-8')))
            payload_to_db(val)
            
            # conn = pymysql.connect(
            # host="192.168.0.101",
            # user="root",
            # password="07101000111",#1sa]Inc]APPisa.db
            # db ='pmsdb',
            # cursorclass = pymysql.cursors.DictCursor
            # )    
            
            # curs = conn.cursor()#vehicle,plate,timein,operator,pic,pic2,lane,pc,exit_log_id
            # sql = '''insert into timeindb   (cardcode,vehicle,plate,timein,operator,lane,pc) values (%s,%s,%s,%s,%s,%s,%s)'''
            # timenow=datetime.now()
            # timenow=timenow.strftime('%Y-%m-%d %H:%M:%S')
            # val = (str(packet.payload.data.decode('utf-8')))

            # curs.execute(sql,val)
            # conn.commit()
            # print(curs.rowcount,'DATA SAVED')
            
       
    except ClientException as ce:
        logger.error("Client exception : %s" % ce)
        
        

def data_exist(tbl, data, cursor):
    dupQuery = ""
    if tbl == "transaction":
        dupQuery = f"SELECT EXISTS(SELECT * FROM {tbl} WHERE or_number = '{data['or_number']}')"
    elif tbl == "tblcaptureimage":
        dupQuery = f"SELECT EXISTS(SELECT * FROM {tbl} WHERE or_number = '{data['trno']}')"
    elif tbl == "timeindb":
        dupQuery = f"EXISTS(SELECT * FROM {tbl} WHERE cardcode = '{data['cardcode']}' and timein = '{data['timein']}')"
    elif tbl == "vip_logs":
        dupQuery = f"EXISTS(SELECT * FROM {tbl} WHERE cardcode = '{data['cardcode']}' and (timein = '{data['timein']}' or timeout = '{data['timein']}'))"
    if len(dupQuery) > 0:  # checks for duplicates in db
        cursor.execute("SELECT " + dupQuery)
        ddata = cursor.fetchone()
        if (ddata[dupQuery] >= 1):  # if duplicate found
            msg = f"Data exists in *{tbl}*: {str(data.values())}"
            print(msg)
            return True
    return False



def payload_to_db(payload):
    conn = pymysql.connect(
            host="10.11.12.50",
            user="isa",
            password="1sa]Inc]APPisa.db",#1sa]Inc]APPisa.db
            db ='pmsdb',
            cursorclass = pymysql.cursors.DictCursor
            )    
 
    if 'tblname' in payload and 'data' in payload:
        # print(payload['tblname'] )
        # print("TYPE OF TBLNAME :",obj('tblname'))
        j = json.loads(payload)
        tbl = j['tblname']  # extract tablename from payload
        
        data = j['data']  # extract data items from payload

        if conn == False:  # exit if mysql connect fails
            print("conenction !True")
            return False
        cursor = conn.cursor()
        if not data_exist(tbl, data, cursor):  # save if no duplicates
            try:
                stmt, vals = dict2sql(tbl, data)
                cursor.execute(stmt, vals)
                conn.commit()
                conn.close()
                print("MySQL data saved")
            except (MySQLdb.Error, MySQLdb.Warning) as e:
                conn.close()
                print(stmt + " failed: " + str(e))
                return False
    else:
        print("Invalid payload format for database")
        return False
    return True

def dict2sql(tbl, data):
    # Compose a string of quoted column names
    cols = ','.join([f'`{k}`' for k in data.keys()])
    # Compose a string of placeholders for values
    vals = ','.join(['%s'] * len(data))
    # Create INSERT SQL statement
    stmt = f'INSERT INTO {tbl} ({cols}) VALUES ({vals})'
    return stmt, tuple(data.values())
if __name__ == '__main__':
    formatter = "[%(asctime)s] :: %(levelname)s :: %(name)s :: %(message)s"
    logging.basicConfig(level=logging.INFO, format=formatter)
    asyncio.get_event_loop().run_until_complete(startBroker())
    asyncio.get_event_loop().run_until_complete(brokerGetMessage())
    asyncio.get_event_loop().run_forever()
    
    
