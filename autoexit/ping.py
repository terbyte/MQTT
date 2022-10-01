import os

def ping_ip(ip):
	stream =os.popen('ping -c 1 {}'.format(ip))
	output =stream.read()
	if '0 received' in output:
		return False
	else:
		return True

