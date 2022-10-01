import asyncio
import websockets
import subprocess
from crt310 import *
from _publish import publisher 
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
TIME_FORMAT = (('%Y-%m-%d %H:%M:%S'))
       
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



def b64_encode_decode(input_string, encode_me):
    b = input_string.encode('UTF-8')
    e = base64.b64encode(b) if encode_me else base64.b64decode(b)
    return e.decode('UTF-8')


def analyze_card(card_data):
	decrypted_data=b64_encode_decode(card_data,False)
	decstr=decrypted_data.split(" ")	
	reference=decstr[0]	
	print("reference ",reference)



	if len(reference)==0:return "NOREF"
	if len(reference)!=12:		
		if len(decstr[3])==10:
			print("reference length [3] ",len(decstr[3]))
			return "VERIFIED"
				
		else:
			print("reference length [3] ",len(decstr[3]))
			return "NOTVERIFIED"


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



    while True:  # loop until users exits from rf operations
        
            while True:  # loop until rfid card is ready
                print('----------------------------------------------')
                # Seek if RFID is present
                if not crt310_seek_rfid(com_handle):
                    print("No valid RFID card present.")
                    
                    
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
                    
                    empty = [0] * (16 * 3) #WRITES 0 FOR VERY BLOCK IN SECTROR
                    
                    

                    _S4Val = crt310_read_mblock(com_handle, 4, 0, 3)
                    _S3Val = crt310_read_mblock(com_handle, 3, 0, 3)
                    print("S4 VALUE  : ",_S4Val)
                    if str2int(_S4Val)== empty:
                        print("S4 IS EMPTY")
                        # IF S3 IS HAS VALUE IT WILL PROCEED / VALID
                        if not crt310_verify_sector_password(com_handle, 3):
                                print("Sector password verification: Failed!")
                                crt310_release_card(com_handle)
                                break
                        if str2int(crt310_read_mblock(com_handle, 3, 0, 3)) == empty: # changet toif s3 is divided by 5
                            print("S3 IS EMPTY")
                            print("INVALID CARD S3")
                            print("\nREJECTED")
                            crt310_release_card(com_handle)
                            break
                       
                        
                        else:
                            
                            #Publish to MQTT timeindb_b 
                            cardcodes =crt310_get_cardcode(com_handle)
                            s3encoded = crt310_read_mblock(com_handle, 3, 0, 3)
                            result=analyze_card(s3encoded) 
                            print("RESULT : ",result)
                            if result.strip() == "VERIFIED":
                                print("RESULT? : ",result)
                                # publisher(cardcodes)#Get the _publish.py file
                                print("decoded Value of S3: ",(crt310_read_mblock(com_handle, 3, 0, 3)))
                                print("Saving to database...")
                                print("PLEASE GET YOUR CARD")
                                print("BARRIER OPENING...")
                                crt310_release_card(com_handle) # continued open barrier
                                wdata = input("PRESS CTRL+C TO EXIT:")
                                break
                            
                            elif result.strip() == "NOTVERIFIED":
                                print("CARD NOT VERIFIED")
                                crt310_release_card(com_handle) # continued open barrier
                                wdata = input("PRESS CTRL+C TO EXIT:")
                                break

                            elif result.strip() == "NOREF":
                                print("CARD HAS NO REFERENCE/EMPTY OT SOMETHING")
                                crt310_release_card(com_handle) # continued open barrier
                                wdata = input("PRESS CTRL+C TO EXIT:")
                                break
                            else:
                                print("UNKNOWN REASON")
                                crt310_release_card(com_handle) # continued open barrier
                                wdata = input("PRESS CTRL+C TO EXIT:")
                                break
                    
                    
                    else:
                        
                        print("CARD ALREADY TRANSACTED")

                        print("\nREJECTED")
                        crt310_release_card(com_handle)#change to reject
                        wdata = input("PRESS CTRL+C TO EXIT:")
                        break
                        
                    wdata = input("PRESS CTRL+C TO EXIT:")

































