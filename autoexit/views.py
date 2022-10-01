import json
import os
import subprocess
import re
import pathlib
import datetime
import cv2
import os
import base64
import pytz
from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.http.response import StreamingHttpResponse
from django.db.models import Q
from django.template.loader import render_to_string
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime, timedelta
from ftplib import FTP
from .crypt import *
from .ping import *
from .camera import *
from .publisher_mqtt import *
from .models import *
from .crt310 import *

# PyAutoGUI - these must be invoked before "import pyautogui"
try:
    os.environ['DISPLAY'] = ':0'  # fixes: "KeyError: 'DISPLAY'"
    os.environ['HOME'] = os.path.expanduser('~')	# fixes: XauthError: $HOME not set
    import pyautogui
except Exception as e:
    print("pyautogui import failed:", e)

settings_json=pathlib.Path().absolute() /'autoexit'/'static'/'set.json'
admin_json=pathlib.Path().absolute() /'autoexit'/'admin.json'
snaps_folder=pathlib.Path().absolute()/'autoexit'/'static'/'snaps'


#SETTINGS FROM JSON
with open(settings_json) as json_file:
	data=json.load (json_file)
	json_file.close()
server_IP=data['server']
com=data['com']
baud=data['baud']
com_=data['com_']
baud_=data['baud_']
is_read=data['is_read']
single_only=data['single_only']
loop_car=data['loop_car']
loop_motor=data['loop_motor']
button_car=data['button_car']
button_motor =data['button_motor']
help_button=data['help_button']
help_car=data['help_car']
help_motor=data['help_motor']
vehicle_in_front =data['vehicle_in_front']
barrier_pin=data['barrier_pin']
logo=data['logo']
ads=data['ads']
announcement=data['announcement']
vehicle_view=data['vehicle_view']
driver_view=data['driver_view']
lpr=data['lpr']
cam_front =data['cam_front']
cam_rear =data['cam_rear']
cam_face =data['cam_face']
channel_front =data['channel_front']
channel_rear =data['channel_rear']
channel_face =data['channel_face']
cam_username =data['cam_username']
cam_password =data['cam_password']
zone_name=data['zone_name']
zone_number=data['zone_number']
ftp_ip=data['ftp_ip']
ftp_username=data['ftp_username']
ftp_password=data['ftp_password']
enc_key=data['enc_key']
siteID=data['siteID']
zoneID=data['zoneID']
exit_GP=data['exit_GP']
noloop=data['noloop']

def crt_check(request):	
	if com=="COM1":comhandle=crt310_open(COM1)
	if com=="COM2":comhandle=crt310_open(COM2)
	if com=="COM3":comhandle=crt310_open(COM3)
	if com=="COM4":comhandle=crt310_open(COM4)
	com_handle=comhandle
	request.session['com_handle']=com_handle	
	
	print(f'com_handle:{comhandle}, com:{com}')
	result=crt310_initialize(com_handle, 0)
	print(f'crt310_initialize: {result}')
	result_check=result
		
	if result_check==True :
		status="CRT-OK"
	else:
		status="CRT-Error"
	return HttpResponse(json.dumps(status),content_type="application/json") 


def b64_encode_decode(input_string, encode_me):
    b = input_string.encode('UTF-8')
    e = base64.b64encode(b) if encode_me else base64.b64decode(b)
    return e.decode('UTF-8')


@csrf_exempt
def read_qr(request):	
	try:
		qrstr=request.POST.get("qrstr","")
		request.session['qrstr']=qrstr
		if qrscanned(qrstr)==True:return HttpResponse(json.dumps("USED"),content_type="application/json") 
		decrypted_qr=b64_encode_decode(qrstr,False)
		decstr=decrypted_qr.split(" ")
		reference=decstr[0]
		if len(reference)!=12:
			if len(decstr[3])!=10:return HttpResponse(json.dumps("NOTVERIFIED"),content_type="application/json")
			entrytimein=datetime.utcfromtimestamp(int(decstr[3])).strftime('%Y-%m-%d %H:%M:%S')
			timenow=datetime.now()
			timenow=timenow.strftime('%Y-%m-%d %H:%M:%S')
			d1=datetime.strptime(timenow,'%Y-%m-%d %H:%M:%S')
			d2=datetime.strptime(entrytimein,'%Y-%m-%d %H:%M:%S')
			diff=d1-d2
			total_minutes=diff.total_seconds()/60
			if float(exit_GP)>=total_minutes:
				timeout=datetime.now(pytz.timezone('Asia/Manila'))			
				save_scannedqr(qrstr,timeout)
				return HttpResponse(json.dumps("GP"),content_type="application/json")
		request.session['reference']=reference
		txntime=datetime.utcfromtimestamp(int(decstr[3])).strftime('%Y-%m-%d %H:%M:%S')
		entryID=reference[0:2].strip("0")
		entryREF=reference[-10:]		
		entryTIME=datetime.utcfromtimestamp(int(entryREF)).strftime('%Y-%m-%d %H:%M:%S')
		request.session['entryID']=entryID
		request.session['entryREF']=entryREF
		timenow=datetime.now()
		timenow=timenow.strftime('%Y-%m-%d %H:%M:%S')		
		d1=datetime.strptime(timenow,'%Y-%m-%d %H:%M:%S')
		d2=datetime.strptime(txntime,'%Y-%m-%d %H:%M:%S')
		diff=d1-d2
		total_minutes=diff.total_seconds()/60
		timeout=datetime.now(pytz.timezone('Asia/Manila'))
		exit_time=timeout.strftime('%Y%m%d%H%M%S')
		request.session['exit_time']=exit_time
		if float(exit_GP)>=total_minutes:			
			#save_scannedqr(qrstr,timeout)
			result="VERIFIED"
		else:
			n=round(float(exit_GP))
			correct_timeout=d2+timedelta(minutes=n)		
			correct_timeout=correct_timeout.strftime('%Y-%m-%d %H:%M:%S')
			dc=datetime.strptime(correct_timeout,'%Y-%m-%d %H:%M:%S')
			diff_excess=(d1-dc)
			total_excess=round(diff_excess.total_seconds()/60)	
			result="EXCEEDED"+ "," + str(total_excess) + "," + txntime
	except Exception as e:
		print(str(e))	
		result="INVALID"
	return HttpResponse(json.dumps(result),content_type="application/json") 


def qrscanned(qrcode):
	qs=scanned_qr.objects.filter(qrcode=qrcode)
	result=qs.exists()
	return result


def save_scannedqr(qrcode,time_scanned):
	qs=scanned_qr(qrcode=qrcode,time_scanned=time_scanned)
	qs.save()


def delete_from_timein(request):
	try:
		entryID=request.session.get('entryID')
		entryREF=request.session.get('entryREF')		
		qs=timeindb.objects.filter(cardcode=entryREF,pc=entryID).delete()	
		return HttpResponse(json.dumps(1),content_type="application/json")
	except Exception as e:		
		return HttpResponse(json.dumps(0),content_type="application/json")


def delete_from_scanned(request):
	yesterday=datetime.now(pytz.timezone('Asia/Manila'))-timedelta(days=1)	
	try:
		qs=scanned_qr.objects.filter(time_scanned__lte=yesterday).delete()		
		return HttpResponse(json.dumps(1),content_type="application/json")
	except Exception as e:		
		return HttpResponse(json.dumps(0),content_type="application/json")


def connected_qrreader(request):
	result=0
	try:
		device_re = re.compile(b"Bus\s+(?P<bus>\d+)\s+Device\s+(?P<device>\d+).+ID\s(?P<id>\w+:\w+)\s(?P<tag>.+)$", re.I)
		df = subprocess.check_output("lsusb")
		devices = []
		for i in df.split(b'\n'):
			if i:
				info = device_re.match(i)
				if info:
					dinfo = info.groupdict()
					devices.append(dinfo)	    
		for device in devices:
		    mytag="Youjie by Honeywell"
		    mytag2="Metrologic Instruments 1470g"
		    tags=device['tag'].decode("utf-8")
		    if mytag in tags:
		       result+=1
		    if mytag2 in tags:
		       result+=1
	except:
		result=0
	return HttpResponse(json.dumps(result),content_type="application/json")


def sendF11(request):
	pyautogui.press("F11")
	return HttpResponse(json.dumps(0),content_type="application/json") 


def home(request):	
	return render(request, 'index.html')


def login(request):
	return render(request,'loginv10.html')


def machine_unavailable(request):
	return render(request,'machine_unavailable.html')


def startup(request):
	return render(request,'startup.html')


def noreader(request):
	return render(request,'noreader.html')


def isValid_datetime(datetime_string):
	format = "%Y-%m-%d %H:%M:%S"
	try:
		datetime.strptime(datetime_string, format)
		return True
	except ValueError:
		return False


def isBlank (myString):
	enc_key_3=enc_key*3
	if enc_key_3[0:48] == myString[0:48]:
		print(f'mystring48: {myString[0:48]}')
		print(f'enc_key3:   {enc_key_3[0:48]}')
		return True
	if myString== "".ljust(48," "):
		return True
	return False


def restart_machine(request):
	result=os.system("sudo reboot now")
	return HttpResponse(json.dumps(result), content_type="application/json")


def shutdown_machine(request):
	result=os.system("sudo shutdown now")
	return HttpResponse(json.dumps(result), content_type="application/json")


@csrf_exempt
def mqtt_logs(request):
	rqdata=request.POST.get("mqtt_msg","")
	print("rqdata:" + rqdata)
	result=send_mqttLogs(server_IP,"Dispenser_Data",rqdata)	
	return HttpResponse(json.dumps(result), content_type="application/json")


@csrf_exempt
def machine_status(request):
	rqdata=request.POST.get("mqtt_msg","")
	result=send_mqttLogs(server_IP,zone_name,rqdata)
	return HttpResponse(json.dumps(result), content_type="application/json")


def camera_connect(request):
	print(f"camera_connect: "+str(cap))
	return HttpResponse(json.dumps(str(cap)), content_type="application/json")


def check_folder(folder):
    return os.path.isdir(folder)


def snapshot(request):
	try:
		if not check_folder(snaps_folder):
			os.makedirs(snaps_folder)
		cap = cv2.VideoCapture(get_rtsp_str(cam_front, channel_front))		
		ret, img = cap.read()
		reference=request.session.get('reference')
		exit_time=request.session.get('exit_time')
		x = reference+"_OUT_"+exit_time
		fname = str(x)+".jpg"
		fpath = str(pathlib.Path().absolute()) + '/autoexit/static/snaps'
		cv2.imwrite(fpath+'/' + fname, img)
		x = "SNAPSHOT_OK"
	except:
		fname=""
		x = "SNAPSHOT_ERROR"
	return HttpResponse(json.dumps(str(x)), content_type="application/json")


def faceshot(request):
	try:
		if not check_folder(snaps_folder):
			os.makedirs(snaps_folder)
		cap = cv2.VideoCapture(get_rtsp_str(cam_face, channel_face))
		time_in = request.POST.get("time_in", "")
		ret, img = cap.read()
		reference=request.session.get('reference')
		exit_time=request.session.get('exit_time')
		x = reference+"_SNAP_"+exit_time	
		fname = str(x)+".jpg"
		fpath = str(pathlib.Path().absolute()) + '/autoexit/static/snaps'
		cv2.imwrite(fpath+'/' + fname, img)
		x = "FACESHOT_OK"
	except:
		fname=""
		x = "FACESHOT_ERROR"
	return HttpResponse(json.dumps(str(x)), content_type="application/json")


@csrf_exempt
def get_plate(request):
	plate="-"
	try:
		ftp = FTP(ftp_ip)
		ftp.login(user=ftp_username,passwd=ftp_password)
		print("FTP")
		dirName ='/'
		ftp.cwd(dirName)
		files = ftp.nlst()
		filename= sorted(files, key=lambda x: ftp.voidcmd(f"MDTM {x}"))[-1]
		time_plate = filename.split("_")
		plate_jpg= time_plate[1].split(".")
		plate= plate_jpg[0]
		print(plate)
		ftp.delete(filename)
		ftp.close()
	except:
		plate="-"
		ftp.close()
	return HttpResponse(json.dumps(plate), content_type="application/json")


@csrf_exempt
def get_plate_rear(request):
	plate="-"
	try:
		ftp = FTP(ftp_ip)
		ftp.login(user=ftp_username,passwd=ftp_password)
		print("FTP")
		dirName ='/'
		ftp.cwd(dirName)
		files = ftp.nlst()
		filename= sorted(files, key=lambda x: ftp.voidcmd(f"MDTM {x}"))[-1]
		time_plate = filename.split("_")
		plate_jpg= time_plate[1].split(".")
		plate= plate_jpg[0]
		print(plate)
		ftp.delete(filename)
		ftp.close()
	except:
		plate="-"
		ftp.close()
	return HttpResponse(json.dumps(plate), content_type="application/json")


def get_rtsp_str(ip,channel):
	return "rtsp://"+cam_username+":"+cam_password+"@"+ip+":554/Streaming/Channels/"+channel+"01"


def get_settings():
	with open(settings_json) as json_file:
		data=json.load(json_file)
		json_file.close()
	com=data['com']
	baud=data['baud']
	com_=data['com_']
	baud_=data['baud_']
	is_read=data['is_read']
	single_only=data['single_only']
	loop_car=data['loop_car']
	loop_motor=data['loop_motor']
	button_car=data['button_car']
	button_motor =data['button_motor']
	help_button=data['help_button']
	help_car=data['help_car']
	help_motor=data['help_motor']
	vehicle_in_front =data['vehicle_in_front']
	barrier_pin=data['barrier_pin']
	logo=data['logo']
	ads=data['ads']
	announcement=data['announcement']
	vehicle_view=data['vehicle_view']
	driver_view=data['driver_view']
	lpr=data['lpr']
	cam_front =data['cam_front']
	cam_rear =data['cam_rear']
	cam_face =data['cam_face']
	channel_front =data['channel_front']
	channel_rear =data['channel_rear']
	channel_face =data['channel_face']
	cam_username =data['cam_username']
	cam_password =data['cam_password']
	zone_name=data['zone_name']
	zone_number=data['zone_number']
	server_IP=data['server']
	ftp_ip=data['ftp_ip']
	ftp_username=data['ftp_username']
	ftp_password=data['ftp_password']
	enc_key=data['enc_key']
	siteID=data['siteID']
	zoneID=data['zoneID']
	exit_GP=data['exit_GP']
	noloop=data['noloop']
	context={'com':com,'baud':baud,
			'com_':com_, 'baud_':baud_,
			'loop_car':loop_car,'loop_motor':loop_motor,
			'button_car':button_car,'button_motor':button_motor,
			'is_read': is_read, 'single_only':single_only,
			'help_button':help_button,'help_car':help_car,'help_motor':help_motor,
			'vehicle_in_front':vehicle_in_front,'barrier_pin':barrier_pin,
			'logo':logo,'ads':ads, 'announcement':announcement,
			'vehicle_view':vehicle_view,'driver_view':driver_view,'lpr':lpr,
			'cam_front':cam_front,'cam_rear':cam_rear,'cam_face':cam_face,
			'channel_front':channel_front,'channel_rear':channel_rear,'channel_face':channel_face,
			'cam_username':cam_username,'cam_password':cam_password,
			'zone_name':zone_name,'zone_number':zone_number,
			'server_IP':server_IP,'ftp_ip':ftp_ip,'ftp_username':ftp_username,'ftp_password':ftp_password,
			'enc_key':enc_key,'siteID':siteID,'zoneID':zoneID,'exit_GP':exit_GP,
			'noloop':noloop,
			}
	return context


def settings(request):
	req_username=request.POST.get('username',"")
	req_password=request.POST.get('password',"")
	with open(admin_json) as f:
		data=json.load(f)
		f.close()
	username=data['username']
	password=data['password']
	if((req_username==username) and (req_password==password)):
		context=get_settings()
		return render(request, 'dashboard.html', context)
	return render(request,'loginv10.html', {'error':'error'})


def dashboard(request):
	return render(request,'dashboard.html')


def settings_crt(request):
	with open(settings_json) as json_file:
		data=json.load(json_file)
		json_file.close()
	com=data['com']
	baud=data['baud']
	com_=data['com_']
	baud_=data['baud_']
	is_read=data['is_read']
	single_only=data['single_only']
	enc_key=data['enc_key']
	context={'com':com,'baud':baud,
				'com_':com_, 'baud_':baud_,
				'is_read': is_read, 'single_only':single_only,
				'enc_key':enc_key,
				}		
	return render(request,'settings/crt.html',context)


def settings_input_output(request):
	with open(settings_json) as json_file:
		data=json.load(json_file)
		json_file.close()
	loop_car=data['loop_car']
	loop_motor=data['loop_motor']
	button_car=data['button_car']
	button_motor =data['button_motor']
	help_button=data['help_button']
	help_car=data['help_car']
	help_motor=data['help_motor']
	vehicle_in_front =data['vehicle_in_front']
	barrier_pin=data['barrier_pin']
	context={'loop_car':loop_car,'loop_motor':loop_motor,
				'button_car':button_car,'button_motor':button_motor,
				'help_button':help_button,'help_car':help_car,'help_motor':help_motor,
				'vehicle_in_front':vehicle_in_front,'barrier_pin':barrier_pin,
				}
	return render(request,'settings/input_output.html',context)


def settings_system_folder(request):
	with open(settings_json) as json_file:
		data=json.load(json_file)
		json_file.close()
	logo=data['logo']
	ads=data['ads']
	announcement=data['announcement']
	vehicle_view=data['vehicle_view']
	driver_view=data['driver_view']
	lpr=data['lpr']
	context={'logo':logo,'ads':ads, 'announcement':announcement,
		'vehicle_view':vehicle_view,'driver_view':driver_view,'lpr':lpr, }
	return render(request,'settings/system_folders.html',context)


def settings_zone(request):
	with open(settings_json) as json_file:
		data=json.load(json_file)
		json_file.close()
	zone_name=data['zone_name']
	zoneID=data['zoneID']
	server_IP=data['server']
	context={'zone_name':zone_name, 'zoneID': zoneID, 'server_IP':server_IP, }
	return render(request,'settings/zone.html',context)


def settings_camera(request):
	with open(settings_json) as json_file:
		data=json.load(json_file)
		json_file.close()
	cam_front =data['cam_front']
	cam_rear =data['cam_rear']
	cam_face =data['cam_face']
	channel_front =data['channel_front']
	channel_rear =data['channel_rear']
	channel_face =data['channel_face']
	cam_username =data['cam_username']
	cam_password =data['cam_password']
	context={'cam_front':cam_front,'cam_rear':cam_rear,'cam_face':cam_face,
		'channel_front':channel_front,'channel_rear':channel_rear,'channel_face':channel_face,
		'cam_username':cam_username,'cam_password':cam_password, }
	return render(request, 'settings/camera.html',context)


def settings_ticket(request):
	with open(settings_json) as json_file:
		data=json.load(json_file)
		json_file.close()
	headerline1 =data['headerline1']
	headerline2 =data['headerline2']
	footerline1 =data['footerline1']
	footerline2 =data['footerline2']
	qrlogo =data['qrlogo']
	qrsize =data['qrsize']
	print_logo =data['print_logo']
	context={'headerline1':headerline1,'headerline2':headerline2,
		'footerline1':footerline1,'footerline2':footerline2,
		'qrlogo':qrlogo,'qrsize':qrsize,'print_logo':print_logo}
	return render(request, 'settings/ticket.html',context)


def video_page_front(request):
	req_ip=request.POST.get("ip","")
	print("req_ip:",req_ip)
	if ping_ip(req_ip)==False:
		print("ping_ip:", ping_ip(req_ip))
		return render(request,'settings_return.html')
	with open(settings_json) as json_file:
		data=json.load(json_file)
		json_file.close()
	username=data['cam_username']
	password=data['cam_password']
	ip=data['cam_front']
	channel=data['channel_front']
	rtsp_str ="rtsp://"+username+":"+password+"@"+ip+":554/Streaming/Channels/"+channel+"01"
	if cam_okay(rtsp_str)==False:
		return render(request,'settings_return.html')
	return render(request, 'video_front.html')


def video_page_rear(request):
	return render(request, 'video_rear.html')


def video_page_face(request):
	return render(request, 'video_face.html')


def video_front(request):
	with open(settings_json) as json_file:
		data=json.load(json_file)
		json_file.close()
	username=data['cam_username']
	password=data['cam_password']
	ip=data['cam_front']
	channel=data['channel_front']
	rtsp_str ="rtsp://"+username+":"+password+"@"+ip+":554/Streaming/Channels/"+channel+"01"
	print("video_front:",rtsp_str)
	if ping_ip(ip)==False:
		print("ping_ip:",ping_ip(ip))
		return render(request,'settings/camera.html')
	if cam_okay(rtsp_str)==False:
		return render(request,'settings/camera.html')
	return StreamingHttpResponse(gframe(rtsp_str),content_type='multipart/x-mixed-replace; boundary=frame')
	

def video_rear(request):
	with open(settings_json) as json_file:
		data=json.load(json_file)
		json_file.close()
	username=data['cam_username']
	password=data['cam_password']
	ip=data['cam_rear']
	channel=data['channel_rear']
	rtsp_str ="rtsp://"+username+":"+password+"@"+ip+":554/Streaming/Channels/"+channel+"01"
	print("video_rear:",rtsp_str)
	return StreamingHttpResponse(gframe(rtsp_str),content_type='multipart/x-mixed-replace; boundary=frame')


def video_face(request):
	with open(settings_json) as json_file:
		data=json.load(json_file)
		json_file.close()
	username=data['cam_username']
	password=data['cam_password']
	ip=data['cam_face']
	channel=data['channel_face']
	rtsp_str ="rtsp://"+username+":"+password+"@"+ip+":554/Streaming/Channels/"+channel+"01"
	print("video_face:",rtsp_str)
	return StreamingHttpResponse(gframe(rtsp_str),content_type='multipart/x-mixed-replace; boundary=frame')


def settings_toJS(request):
	allsettings=get_settings()
	# print(allsettings)
	return HttpResponse(json.dumps(allsettings),content_type="application/json")


@csrf_exempt
def save_settings_request(request):
	param=request.POST.get("key","")
	value=request.POST.get("value","")
	modify_json(param,value)
	return HttpResponse(json.dumps(value), content_type="application/json")


def modify_json(key, value):
	with open(settings_json) as json_file:
		data = json.load(json_file)
		json_file.close()
		tmp = data[key]
		data[key] = value
		jsonfile = open(settings_json, 'w+')
		jsonfile.write(json.dumps(data))
		jsonfile.close()

def seek_card(request):
	com_handle=request.session.get('com_handle')
	if crt310_seek_rfid(com_handle):
		result=1
	else:
		result=0
	return HttpResponse(json.dumps(result),content_type="application/json") 

def release_card(request):
	com_handle=request.session.get('com_handle')
	if crt310_seek_rfid(com_handle)==True:
		if  crt310_release_card(com_handle):
			result="release card okay"
		else:
			reuslt="release card failed"
	else:
		result="NoCard"
	return HttpResponse(json.dumps(result),content_type="application/json") 

