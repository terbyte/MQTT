import asyncio
import websockets
import subprocess
from crt310 import *
import base64
import datetime
from datetime import datetime, timedelta
import pytz
import json
import pathlib
from pathlib import Path

import time
settings_json=Path(pathlib.Path().absolute()).parents[0] /'autoexit'/'static'/'set.json'
print(f'settings_json={settings_json}')

with open(settings_json) as json_file:
	data=json.load (json_file)
	json_file.close()
com=data['com']
com_=data['com_']
exit_GP=data['exit_GP']

IP_ADDRESS='127.0.0.1'
CRT310_PORT=5680
SLEEP_TIME=0.1
    
       
lib310 = load_crt310_dll()                           # load DLL
if com=="COM1":com_handle=crt310_open(COM1)
if com=="COM2":com_handle=crt310_open(COM2)
if com=="COM3":com_handle=crt310_open(COM3)
if com=="COM4":com_handle=crt310_open(COM4)


if crt310_initialize(com_handle,0):
	print(f"connected @ {com}, com_handle:{com_handle}")
else:
	print(f"NOT connected @ {com}, com_handle:{com_handle}")
	subprocess.run(["/usr/bin/notify-send", "--icon=dialog-warning", f"Cannot connect @ {com}"]) 


def crt310_sensor_status(port_fd):
    _, rxdata = crt310_execute_cmd(com_handle, [0x31, 0x2F])
    if rxdata[0] == 78:  # int 78 = hex 4e = ascii 'N'; NEGATIVE
        error_desc = crt310_error(rxdata[1])
        logger.error("crt310_sensor_status: error=" + error_desc)
        return error_desc
    sensor_status = rxdata[2:].hex()
    logger.info("crt310_sensor_status:" + sensor_status)
    return sensor_status

def analyze_card(card_data):
	decrypted_data=b64_encode_decode(card_data,False)
	decstr=decrypted_data.split(" ")	
	reference=decstr[0]	
	print("reference ",reference)

	if len(reference)==0:return "NOREF"
	if len(reference)!=12:		
		if len(decstr[3])!=10:
			print("reference length [3] ",len(decstr[3]))
			return "NOTVERIFIED"
				
		entrytimein=datetime.utcfromtimestamp(int(decstr[3])).strftime('%Y-%m-%d %H:%M:%S')		
		timenow=datetime.now()		
		timenow=timenow.strftime('%Y-%m-%d %H:%M:%S')
		d1=datetime.strptime(timenow,'%Y-%m-%d %H:%M:%S')
		d2=datetime.strptime(entrytimein,'%Y-%m-%d %H:%M:%S')
		diff=d1-d2
		total_minutes=diff.total_seconds()/60			
		
	txntime=datetime.utcfromtimestamp(int(decstr[3])).strftime('%Y-%m-%d %H:%M:%S')	
	entryID=reference[0:2].strip("0")	
	entryREF=reference[-10:]

	entryTIME=datetime.utcfromtimestamp(int(entryREF)).strftime('%Y-%m-%d %H:%M:%S')	
	timenow=datetime.now()
	timenow=timenow.strftime('%Y-%m-%d %H:%M:%S')		
	d1=datetime.strptime(timenow,'%Y-%m-%d %H:%M:%S')
	d2=datetime.strptime(txntime,'%Y-%m-%d %H:%M:%S')
	diff=d1-d2
	total_minutes=diff.total_seconds()/60
	timeout=datetime.now(pytz.timezone('Asia/Manila'))
	exit_time=timeout.strftime('%Y%m%d%H%M%S')
	
	if float(exit_GP)>=total_minutes:		
		print("VERIFIED FROM EXIT_GP > TOTAL_MINUTES")
		return "GP"
	else:
		n=round(float(exit_GP))
		correct_timeout=d2+timedelta(minutes=n)		
		correct_timeout=correct_timeout.strftime('%Y-%m-%d %H:%M:%S')
		dc=datetime.strptime(correct_timeout,'%Y-%m-%d %H:%M:%S')
		diff_excess=(d1-dc)
		total_excess=round(diff_excess.total_seconds()/60)		
		result="EXCEEDED TIME: "+ "," + str(total_excess) + "," + txntime
		return "EXCEEDED"

def b64_encode_decode(input_string, encode_me):
    b = input_string.encode('UTF-8')
    e = base64.b64encode(b) if encode_me else base64.b64decode(b)
    return e.decode('UTF-8')


if __name__ == "__main__":
    print("\n=== CRT-310 card capturer DEMO ===")
    logger = set_logger("crt310.log")  # set log filename
    lib310 = load_crt310_dll()  # load DLL

    com_handle = crt310_open(COM2)  # open com port
    # com_handle = crt310_open(USB0)    # open com port

    # initialize CRT
    if crt310_initialize(com_handle, 0):
        print("Initialize : OK")
    else:
        print("CRT-310 initialization failed!  \nBye, bye!")
        sys.exit()

    # get crt-310 s/n
    _, rxdata = crt310_execute_cmd(com_handle, [0x30, 0x3A])
    if rxdata[0] == 78:  # int 78 = hex 4e = ascii 'N'; NEGATIVE
        error_desc = crt310_error(rxdata[1])
        logger.error("TX310_GET_SNO: error=" + error_desc)
        print("CRT-310 S/N:", error_desc)
    else:
        print("CRT-310 S/N:", rxdata[3:].decode("utf-8"))

    # display crt-310 device status
    print("Device status:", crt310_device_status(com_handle))

    # display crt-310 sensor status
    print("Sensor status:", crt310_sensor_status(com_handle))


    card_data = crt310_read_mblock(com_handle, 4, 0, 3)
    while True:  # loop until users exits from rf operations
        
            while True:  # loop until rfid card is ready
                print('----------------------------------------------')
                # Seek if RFID is present
                if not crt310_seek_rfid(com_handle):
                    print("No valid RFID card present.")
                    
                    
                print("\nPerforming Multi-block card operations")
                print("\nPlease Insert Card")
                while True:  # loop until users exits from multiblock operations
                    while True:  # loop until rfid card is ready
                        # Seek if RFID is present
                        if not crt310_seek_rfid(com_handle):

                            # input("### Please insert card, then press <Enter> to continue...")
                            continue
                        else:
                            break
            
                    # display rf cardcode (s/n or uid)
                    print("\nCardcode:", crt310_get_cardcode(com_handle))
                    if not crt310_verify_sector_password(com_handle, 4):
                        print("Sector password verification: Failed!")
                        crt310_release_card(com_handle)
                        break

                    _S4Val = crt310_read_mblock(com_handle, 4, 0, 3)
                    empty = [0] * (16 * 3)
                    print("EXISTING S4 VALUE: ",_S4Val)
                    #check if S4 is valid/ valid when may laman

                    cardcodes =crt310_get_cardcode(com_handle)
                    s4encoded = crt310_read_mblock(com_handle, 4, 0, 3)
                    result=analyze_card(s4encoded) 

                    print("RESULT? : ",result)
                    

                    #IF S4 IS VALID  [S3] == 10
                    
                    if result.strip() == "VERIFIED" or result.strip() =='GP' :#S4 IS VALID  [S3] == 10

                        print("S4 IS VALID")
                        print("CHECKING IF UNDER GRACE PERIOD...")
                        #CHECK IF PARKER'S STILL UNDER GRACE PERIOD
                        

                        # if result.strip() == 'EXCEEDED':#static change to dynamic once ready
                        print("Under grace period.")
                        print("Please get your card.")
                        crt310_release_card(com_handle)#EJECT CARD
                        print("MQTT-PUBLISHING EXITLOG_B")
                        #MQTT-PUBLISH EXITLOG_B
                        print("BARRIER OPENING...")
                        
                        else:
                            print("NO LONGER UNDER GRACE PERIOD,PAYMENT REQUIRED")
                            crt310_release_card(com_handle)#REJECT CARD
                            print("CARD REJECTED")
                        
                    
                    elif result.strip() == "NOTVERIFIED":
                        print("CARD NOT VERIFIED")
                    else:
                        
                        print("CARD HAS UNSETTLED PAYMENT")

                        print("\nREJECTED")
                        crt310_release_card(com_handle)#change to reject
                        
                        # break
                    wdata = input("PRESS CTRL+C TO EXIT:")























# if not crt310_verify_sector_password(com_handle, 3):
#                             print("Sector password verification: Failed!")
#                             break
#                         if (crt310_read_mblock(com_handle, 3, 0, 3)) == 'VALID':
#                             print("SECTOR 3 is VALID")
#                             #Publish to MQTT timeindb_b
#                             print("PLEASE GET YOUR CARD")
#                             print("BARRIER OPENING")
                            
#                             crt310_release_card(com_handle) # continued open barrier













