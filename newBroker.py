import paho.mqtt.client as mqtt
import MySQLdb.cursors
import os
import sys
import json
import logging

# Constants for MQTT Broker connection
MQTT_SERVER = "10.11.12.50"
MQTT_USER = "isamqtt"
MQTT_PASS = "1sa[mqttLogger]"
MQTT_PORT = 1883  # default
# topic url; all topics intended for "dbdata"
MQTT_URL = ("pms/entry/pmsdis002/dbdata")
# ("pms/entry/pmsdis002/dbdata")

# Constants for MySQL connection
DB_HOST = "localhost"
DB_USER = "root"
DB_PASS = "07101000111"
DB_NAME = "pmsdb"

# Logger settings
logpath = "/srv/log"
logfile = "mqtt2mysql.log"
# loglevel = logging.INFO
loglevel = logging.WARNING


def set_logger(logfile, loglevel=logging.WARNING):
    """ === Python LOGGING """
    # loglevel = logging.INFO  # adjust as desired
    dtfmt = "%Y-%m-%d %H:%M:%S"  # date/time format
    logfmt = "%(levelname)s: %(asctime)s: %(message)s"  # logging format
    logging.basicConfig(filename=logfile,
                        level=loglevel,
                        format=logfmt,
                        datefmt=dtfmt)
    return logging.getLogger()  # end method and return some values


def db_connect(db=DB_NAME, host=DB_HOST, user=DB_USER, pwd=DB_PASS):
    try:
        conn = MySQLdb.connect(host=host,
                               user=user,
                               password=pwd,
                               db=db,
                               charset='utf8mb4',
                               cursorclass=MySQLdb.cursors.DictCursor)
    except (MySQLdb.Error, MySQLdb.Warning) as e:
        print("MySQL connect failed: " + str(e))
        return False
    return conn


# Converts dictionary keys/values for sql statement
def dict2sql(tbl, data):
    # Compose a string of quoted column names
    cols = ','.join([f'`{k}`' for k in data.keys()])
    # Compose a string of placeholders for values
    vals = ','.join(['%s'] * len(data))
    # Create INSERT SQL statement
    stmt = f'INSERT INTO {tbl} ({cols}) VALUES ({vals})'
    return stmt, tuple(data.values())


# Checks if data already exists
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


# This function saves mqtt payload into mysql
def payload_to_db(payload):
    if 'tblname' in payload and 'data' in payload:
        tbl = payload['tblname']  # extract tablename from payload
        data = payload['data']  # extract data items from payload
        conn = db_connect()
        if conn == False:  # exit if mysql connect fails
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


# The callback for when a PUBLISH message is received from the MQTT Broker.
def on_message(client, userdata, msg):
    print("MQTT data received")
    payload = json.loads((msg.payload).decode("utf-8"))
    status = payload_to_db(payload)  # save payload to db
    return status


# This callback function fires when the MQTT Broker conneciton is established.
# At this point a connection to MySQL server will be attempted.
def on_connect(client, userdata, flags, rc):
    # instantiate topic subscription
    client.subscribe(MQTT_URL)
    print("MQTT connected/subscribed to: " + MQTT_URL)
    # test mysql connection and exit if failed
    conn = db_connect()
    if conn != False:
        conn.close()
        print("MySQL Client Connected")
    else:
        print("Aborting.")
        sys.exit()


####  Main app ####
# Logging


# Connect the MQTT Client
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(username=MQTT_USER, password=MQTT_PASS)

try:
    client.connect(MQTT_SERVER, MQTT_PORT)  #connect to broker
except Exception as e:
    print("MQTT connect failed:" + str(e))
    sys.exit(e)

# Stay connected to the MQTT Broker indefinitely
try:
    client.loop_forever()
except KeyboardInterrupt:
    print("\nCtrl-C pressed.  Terminating gracefully.\n")

# close connection before app exit
print("Terminating gracefully.")
client.disconnect()
