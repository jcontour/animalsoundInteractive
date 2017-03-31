import os

def send2Pd(message=''):
	os.system("echo '" + message + "' | pdsend 3000")

def audioOn():
	message = '0 1;'
	send2Pd(message)

def audioOff():
	message = '0 0;'
	send2Pd(message)

def setVolume():
	vol = 80
	message = '1 ' + str(vol) + ';'
	send2Pd(message)


audioOn()