from django.urls import path,include
from django.conf.urls import url, include
from django.contrib import admin
from . import views
from django.contrib.auth import views as auth_views

urlpatterns =[
	
	path('delete_from_scanned',views.delete_from_scanned,name='delete_from_scanned'),
	path('delete_from_timein',views.delete_from_timein,name='delete_from_timein'),
	path('home',views.home,name='home'),
	path('',views.startup, name='startup'),
	path('connected_qrreader',views.connected_qrreader,name='connected_qrreader'),
	path('crt_check',views.crt_check,name='crt_check'),
	
	path('login',views.login, name='login'),
	path('settings', views.settings, name='settings'),
	path('dashboard',views.dashboard, name='dashboard'),
	path('settings_crt',views.settings_crt,name='settings_crt'),
	path('settings_input_output', views.settings_input_output, name='settings_input_output'),
	path('settings_system_folder', views.settings_system_folder, name='settings_system_folder'),
	path('settings_zone', views.settings_zone, name='settings_zone'),
	path('settings_camera', views.settings_camera, name='settings_camera'),
	path('settings_ticket', views.settings_ticket, name='settings_ticket'),
	path('restart_machine', views.restart_machine, name='restart_machine'),
	path('shutdown_machine', views.shutdown_machine, name='shutdown_machine'),

	path('video_front', views.video_front, name='video_front'),
	path('video_rear', views.video_rear, name='video_rear'),
	path('video_face', views.video_face, name='video_face'),

	path('video_page_front', views.video_page_front, name='video_page_front'),
	path('video_page_rear', views.video_page_rear, name='video_page_rear'),
	path('video_page_face', views.video_page_face, name='video_page_face'),

	
	path('get_plate_rear',views.get_plate_rear,name='get_plate_rear'),
	path('get_plate',views.get_plate,name='get_plate'),
	path('faceshot',views.faceshot,name='faceshot'),
	path('snapshot',views.snapshot, name='snapshot'),
	
	path('machine_status',views.machine_status,name='machine_status'),
	path('mqtt_logs',views.mqtt_logs,name='mqtt_logs'),
	path('shutdown_machine',views.shutdown_machine,name='shutdown_machine'),
	path('restart_machine',views.restart_machine,name='restart_machine'),
	path('settings_toJS',views.settings_toJS,name='settings_toJS'),
	
	path('sendF11',views.sendF11,name='sendF11'),
	path('read_qr',views.read_qr,name='read_qr'),

	path('machine_unavailable',views.machine_unavailable,name='machine_unavailable'),
	path('startup',views.startup,name='startup'),
	path('noreader',views.noreader,name='noreader'),
	path('save_settings_request', views.save_settings_request,name='save_settings_request'),

	path('release_card',views.release_card,name='release_card'),
	path('seek_card',views.seek_card,name='seek_card'),


	# path('exist_timein',views.exist_timein,name='exist_timein'),
	]



