import base64
from datetime import datetime, timedelta
import pathlib
from pathlib import Path
import json
import pytz


settings_json=Path(pathlib.Path().absolute()).parents[0] /'MQTT'/'autoexit'/'static'/'set.json'
print(f'settings_json={settings_json}')
with open(settings_json) as json_file:
	data=json.load (json_file)
	json_file.close()

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'
exit_GP=data['exit_GP']

print(f'\nexit_GP = {exit_GP}')



def b64_encode_decode(input_string, encode_me):
    b = input_string.encode('UTF-8')
    e = base64.b64encode(b) if encode_me else base64.b64decode(b)
    print("\nVALUE: ",e.decode('UTF-8'))
    return e.decode('UTF-8')




def analyze_card(card_data):
    decrypted_data=b64_encode_decode(card_data,False)
    decstr=decrypted_data.split(" ")
    reference=decstr[0]
    
    if len(reference)==0:
        print("NOREM")
    if len(reference)!=12:
        if len(decstr[3])!=10:
            print("NOTVERIFIED")
        
        entrytimein=datetime.utcfromtimestamp(int(decstr[3])).strftime(TIME_FORMAT)
        timenow=datetime.now()
        timenow=timenow.strftime(TIME_FORMAT)
        d1=datetime.strptime(timenow,TIME_FORMAT)
        d2=datetime.strptime(entrytimein,TIME_FORMAT)
        diff=d1-d2
        total_minutes=diff.total_seconds()/60
        
    txntime=datetime.utcfromtimestamp(int(decstr[3])).strftime(TIME_FORMAT)	
    entryID=reference[0:2].strip("0")	
    entryREF=reference[-10:]
    entryTIME=datetime.utcfromtimestamp(int(entryREF)).strftime(TIME_FORMAT)	
    timenow=datetime.now()
    timenow=timenow.strftime(TIME_FORMAT)		
    d1=datetime.strptime(timenow,TIME_FORMAT)
    d2=datetime.strptime(txntime,TIME_FORMAT)
    diff=d1-d2
    total_minutes=diff.total_seconds()/60
    timeout=datetime.now(pytz.timezone('Asia/Manila'))
    exit_time=timeout.strftime('%Y%m%d%H%M%S')
	
    if float(exit_GP)>=total_minutes:		
        return "VERIFIED"
    else:
        n=round(float(exit_GP))
        correct_timeout=d2+timedelta(minutes=n)		
        correct_timeout=correct_timeout.strftime(TIME_FORMAT)
        dc=datetime.strptime(correct_timeout,TIME_FORMAT)
        diff_excess=(d1-dc)
        total_excess=round(diff_excess.total_seconds()/60)	
        result="EXCEEDED"+ "," + str(total_excess) + "," + txntime		
        print(result)
        return result

        
        
        
        
 
 
analyze_card("OTkgOTkgOTk5IDE2MzQzNDM5MDIgOTk=")
















#VALIDATE S4 IF EMPTY AND OR THE VALUE IS DIVIDED BY FIVE
#VALIDATE S3 IF THE 3RD INDEX(4TH ELEMENT) IS EXACTLY 10 DIGITS