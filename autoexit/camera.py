import cv2, os, urllib.request
import numpy as np
from django.conf import settings


def CameraVideo(rtsp_str):
	cam=cv2.VideoCapture(rtsp_str)

	success,imgNp = cam.read()
	resize = cv2.resize(imgNp, (640, 480), interpolation = cv2.INTER_LINEAR)
	ret, jpeg = cv2.imencode('.jpg', resize)
	
	return jpeg.tobytes()


def gframe(rtsp_str):
	while True:
		frame = CameraVideo(rtsp_str)

		yield (b'--frame\r\n'
				b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def cam_okay(rtsp_str):
	cam=cv2.VideoCapture(rtsp_str)
	success,imgNp=cam.read()
	return success
