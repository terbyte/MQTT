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
cardcode = crt310_get_cardcode(com_handle)

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

    # print("\nVALUE: ",e.decode('UTF-8'))
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


    while True:  # loop until users exits from rf operations
        while True:  # loop until rfid card is ready
            # Seek if RFID is present
            if not crt310_seek_rfid(com_handle):

                continue
            else:
                break
        # Multi-block operations (read and write)

        while True:  # loop until users exits from multiblock operations
            while True:  # loop until rfid card is ready
                # Seek if RFID is present
                if not crt310_seek_rfid(com_handle):

                    continue
                else:
                    break

            # display rf cardcode (s/n or uid)
            print("\nCardcode:", crt310_get_cardcode(com_handle))
            
            
            # verify Key-A password
            if not crt310_verify_sector_password(com_handle, 3):
                print("Sector password verification: Failed!")
                break
            
           
            print("S3 VALUE: ",crt310_read_mblock(com_handle, 3, 0, 3))
            print("S3 RAW VALUE",b64_encode_decode(crt310_read_mblock(com_handle, 3, 0, 3),False))
            
            wdatas3 = input("\nWRITE ON S3: ")
            # write multi-block data to rfid
            decoded_wdatas3 = b64_encode_decode(wdatas3,True)
            print("BASE64 VALUE: ",b64_encode_decode(wdatas3,True)," OF ",b64_encode_decode(decoded_wdatas3,False))

  
            card_datas3 = crt310_write_mblock(com_handle, 3, 0, 3, decoded_wdatas3)
        
            print(f"  Multi-block data write operation, success!")
            

            if not crt310_verify_sector_password(com_handle, 4):
                print("Sector password verification: Failed!")
                break
            # multi-block write oprations
            ans = input("\nWrite multi-block data to RFID ? (y/n):")
            if ans.lower() == "y":
                print("s4 VALUE: ",crt310_read_mblock(com_handle, 4, 0, 3))
                print("S4 RAW VALUE",b64_encode_decode(crt310_read_mblock(com_handle, 4, 0, 3),False))
                wdatas4 = input("  Please enter data to write on s4:")
                # write multi-block data to rfid
                decoded_wdataS4 = b64_encode_decode(wdatas4,True)
                print("BASE64 VALUE: ",b64_encode_decode(wdatas4,True)," OF ",b64_encode_decode(decoded_wdataS4,False))
                card_datas3= crt310_write_mblock(com_handle, 4, 0, 3, decoded_wdataS4)


                print(f"  Multi-block data write operation, success!")
                print("s4 VALUE: ",crt310_read_mblock(com_handle, 4, 0, 3))

            if not crt310_verify_sector_password(com_handle, 3):
                print("Sector password verification: Failed!")
                break
            print("\nS3 VALUE : ",crt310_read_mblock(com_handle, 3, 0, 3))

            if not crt310_verify_sector_password(com_handle, 4):
                print("Sector password verification: Failed!")
                break
            print("\nS4 VALUE : ",crt310_read_mblock(com_handle, 4, 0, 3))

            crt310_release_card(com_handle)#change to reject
            ans = input("\nDo you want to do Multiblock operations again? (y/n):")
            if ans.lower() != "y":
                break
    if crt310_close(com_handle) == 0:
        print("\nPort closed properly. \nBye-bye!")
