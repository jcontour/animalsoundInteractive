import os
from gpiozero import Button
from gpiozero import MCP3008

pot = MCP3008(channel=0)

#################### SETUP VARIABLES

increment = 0
currentspeed = 0
volume = 0
maxspeed = 1
minspeed = 0
value = 0
whichLED = 0

#################### FUNCTIONS

def send2Pd(message=''):
	os.system("echo '" + message + "' | pdsend 3333")

def audioSwitcher(num):
	# 0 = bat 1 = bird
	message = '0 ' + str(num) + ';'
	# print message
	send2Pd(message)

def setPlaybackSpeed(val):
	message = '1 ' + str(val) + ';'
	print message
	send2Pd(message)

def setVolume(val):
	# SET THE VOLUME LEVEL
	message = '2 ' + str(val) + ';'
	# print message
	send2Pd(message)

# def setLED(led):
	#do LED things


def remapValues(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)

def calcPlaybackSpeed(val):
	if val < 45:
		global currentspeed
		currentspeed = 0
	elif val >= 45 & val < maxspeed:
		global currentspeed
		currentspeed = remapValues(val, 45, 90, 0, maxspeed)
	else: 
		global currentspeed
		currentspeed = maxspeed
	print("currentspeed: " + str(currentspeed))
	# setPlaybackSpeed(currentspeed)

def calcVolume(val):
	if val < 35 | val > 90:
		global volume
		volume = 0
	elif val >= 35 & val < 45:
		global volume
		volume = remapValues(val, 35, 45, 0, 1)
	elif val >= 90 & val < 100:
		global volume
		volume = remapValues(val, 90, 100, 1, 0)
	else:
		global volume
		volume = 1
	print("volume: " + str(volume))

def calcLED(val):
	global whichLED
	whichLED = remapValues(val, 0, 135, 0 , 45)
	print("led: " + str(whichLED))



def calcValues(val):
	if val < 0:
		val = 0
	elif val > 135:
		val = 135

	print ("current value: " + str(val))

	calcPlaybackSpeed(val)
	calcVolume(val)
	calcLED(val)

button_turnUp = Button(20)
button_turnDown = Button(21)

objs = [
	{"gpioPin": 13, "startSpeed": 0.011, "increment": 0.01, "maxspeed": 0.05},	# BAT
	{"gpioPin": 19, "startSpeed": 0.386, "increment": 0.1, "maxspeed": 1 }		# BIRD
	# {"gpioPin": 26, "startSpeed": 0.386, "increment": 0.1}
]

class Audio:
	def __init__(self, id, gpio_pin, start_speed, increment, maxspeed):
		self.id = id
		self.button = Button(gpio_pin)
		self.start_speed = start_speed
		self.increment = increment
		self.maxspeed = maxspeed

		self.button.when_pressed = self.pressed 

	def pressed(self):
		print("pressed")
		
		#set global values
		global current_audio
		current_audio = self.id
		global increment
		increment = self.increment
		global maxspeed
		maxspeed = self.maxspeed
		global currentspeed
		currentspeed = self.start_speed
		audioSwitcher(self.id)

audiobuttons = []

for index, item in enumerate(objs):
	ab = Audio(index, item["gpioPin"], item["startSpeed"], item["increment"], item["maxspeed"])
	audiobuttons.append(ab)

#################### Main Loop

while (True):
	# IF it's been a while since input, stop playing audio?

	# wait for input from knob, when turned, add/subtract current increment value*degrees turned from current playSpeed

	if (button_turnUp.is_pressed):
		value = value + 1
		if value > 135:
			value = 135
		calcValues(value)
	
	if (button_turnDown.is_pressed):
		value = value - 1
		if value < 0:
			value = 0
		calcValues(value)

		
pause()