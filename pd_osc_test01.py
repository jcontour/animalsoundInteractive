import os
import math
from gpiozero import Button
from gpiozero import MCP3008

pot = MCP3008(channel=0)

#################################################################################################### Setup variables

increment = 0
currentspeed = 0
volume = 0
maxspeed = 1
minspeed = 0
value = 0
whichLED = 0

#################################################################################################### Send messages to PD

def send2Pd(message=''):
	os.system("echo '" + message + "' | pdsend 3333")

def audioSwitcher(num):
	# 0 = bat 1 = bird
	message = '0 ' + str(num) + ';'
	# print message
	send2Pd(message)

def setPlaybackSpeed(val):
	message = '1 ' + str(val) + ';'
	# print message
	send2Pd(message)

def setVolume(val):
	# SET THE VOLUME LEVEL
	message = '2 ' + str(val) + ';'
	# print message
	send2Pd(message)

def pause():
	message = '3 bang;'
	send2Pd(message)

# def setLED(led):
	#do LED things

#################################################################################################### Calculating values to send

def remapValues(inValue, inMin, inMax, outMin, outMax):
	outValue = (((inValue - inMin) * (outMax - outMin)) / (inMax - inMin)) + outMin
	return round(outValue, 3)

def calcPlaybackSpeed(val):
	if val < 45:
		global currentspeed
		currentspeed = 0
	elif val >= 45 and val < 90:
		global currentspeed
		currentspeed = remapValues(val, 45, 90, 0, maxspeed)
	else: 
		global currentspeed
		currentspeed = maxspeed

	setPlaybackSpeed(currentspeed)
	print("currentspeed: " + str(currentspeed))
	# setPlaybackSpeed(currentspeed)

def calcVolume(val):
	if val < 35 or val > 90:
		global volume
		volume = 0
	elif val >= 35 and val < 45:
		global volume
		volume = remapValues(val, 35, 45, 0, 1)
	elif val >= 90 and val < 100:
		global volume
		volume = 1 - remapValues(val, 90, 100, 0, 1)
	else:
		global volume
		volume = 1

	setVolume(volume)
	print("volume: " + str(volume))

def calcLED(val):
	global whichLED

	whichLED = int(math.floor(remapValues(val, 0, 135, 0 , 45)))

	print("led: " + str(whichLED))

def calcValues(val):
	print ("current value: " + str(val))

	calcPlaybackSpeed(val)
	calcVolume(val)
	calcLED(val)

#################################################################################################### Setup Buttoms

button_turnUp = Button(20)
button_turnDown = Button(21)
button_pause = Button(26)

objs = [
	{"gpioPin": 13, "startSpeed": 0.011, "maxspeed": 0.05},		# BAT
	{"gpioPin": 19, "startSpeed": 0.386, "maxspeed": 1 }		# BIRD
	# {"gpioPin": 26, "startSpeed": 0.386, "increment": 0.1}
]

class Audio:
	def __init__(self, id, gpio_pin, start_speed, maxspeed):
		self.id = id
		self.button = Button(gpio_pin)
		self.start_speed = start_speed
		self.maxspeed = maxspeed

		self.button.when_pressed = self.pressed 

	def pressed(self):
		print("pressed")
		
		#set global values
		global current_audio
		current_audio = self.id
		global maxspeed
		maxspeed = self.maxspeed
		calcValues(value)
		audioSwitcher(self.id)

audiobuttons = []

for index, item in enumerate(objs):
	ab = Audio(index, item["gpioPin"], item["startSpeed"], item["maxspeed"])
	audiobuttons.append(ab)

#################################################################################################### Main Loop

while (True):
	# IF it's been a while since input, stop playing audio?

	# wait for input from knob, when turned, add/subtract current increment value*degrees turned from current playSpeed

	if (button_turnUp.is_pressed):
		value = value + 1
		# if value > 135:
			# value = 135
		calcValues(value)
	
	if (button_turnDown.is_pressed):
		value = value - 1
		# if value < 0:
			# value = 0
		calcValues(value)

	if (button_pause.is_pressed):
		pause()

		
pause()

