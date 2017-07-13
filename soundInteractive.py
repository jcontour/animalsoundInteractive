import os
import math
import time
from gpiozero import Button
from gpiozero import MCP3008
import RPi.GPIO as GPIO
from dotstar import Adafruit_DotStar

# - - - setup pixels

numpixels = 45
datapin = 23
clockpin = 24

strip = Adafruit_DotStar(numpixels, datapin, clockpin)

# - - - setup rotary encoder

RoAPin = 17    # pin11
RoBPin = 18    # pin12
RoSPin = 27    # pin13

globalCounter = 0

flag = 0
prev_pos = 0
cur_pos = 0
prev_counter = 0

max_counter = 1000

############################# ----- Setup variables

value = 0				# value that remaps all other variables   		goes from 0-135
prev_value = 0

volume = 0.0
maxspeed = 1
minspeed = 0
whichLED = 0

############################# ----- Send messages to PD

def send2Pd(message=''):
	# os.system("echo '" + message + "' | pdsend 3333")
	print "send to PD " + message

def setAudioClip(num):
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

def pauseAudio():
	message = '3 bang;'
	send2Pd(message)

############################# ----- Calculating values to send

def remapValues(inValue, inMin, inMax, outMin, outMax):
	outValue = (((inValue - inMin) * (outMax - outMin)) / (inMax - inMin)) + outMin
	return round(outValue, 5)

def calcPlaybackSpeed(val):
	global currentspeed
	if val < 45:
		currentspeed = 0
	elif val >= 45 and val < 100:
		currentspeed = remapValues(val, 45, 100, 0, maxspeed)
	else: 
		currentspeed = maxspeed

	setPlaybackSpeed(currentspeed)
	# print("currentspeed: " + str(currentspeed))

def calcVolume(val):
	global volume
	if val < 25 or val > 110:
		volume = 0
	elif val >= 25 and val < 45:
		volume = remapValues(val, 25, 45, 0.1, 1.0)
	elif val >= 90 and val < 110:
		volume = remapValues(val, 90, 110, 1.0, 0.1)
	else:
		volume = 1

	setVolume(volume)
	# print("volume: " + str(volume))

whichLED = 1
prevLED = 2
def setLED(val):
    global whichLED
    global prevLED

    strip.setPixelColor(prevLED, 0)

    prevLED = whichLED
    whichLED = int(remapValues(val, 0, 135, 0, numpixels - 1))
    
    strip.setPixelColor(whichLED, 0x0000FF)
    strip.show()

def calcValues(val):
	# print ("current value: " + str(val))

	calcPlaybackSpeed(val)
	calcVolume(val)
	setLED(val)

############################# ----- Setup time interaction

def clearLights():
	for led in range(numpixels):
		strip.setPixelColor(led, 0)
	strip.show()

# color = 0x0000FF
# idleled = 0

def idleLights():

	for led in range(numpixels):
		strip.setPixelColor(led, 0x0000FF)
	strip.show()

	# ---- way too fast rainbow idle
	# strip.setPixelColor(idleled, color)
	# strip.show()

	# idleled += 1
	# if idleled > numpixels - 1:
	# 	idleled = 0
	# 	color >>= 1

	# if color == 0:
	# 	color = 0xFF0000


timeOfLastAction = 0
isIdle = False

def checkTime(buttonTime):
	# print("elapsed time: " + str(time.time() - buttonTime))
	if time.time() - buttonTime > 5:
		global isIdle
		isIdle = True
		pauseAudio()

def startupSequence():
	colors = [0x009900, 0x999900, 0x990000, 0]
	for color in colors:
		for led in range(numpixels):
			strip.setPixelColor(led, color)
			strip.show()
			time.sleep(0.3 / 50)


############################# ----- Setup Buttoms

def setup():
	GPIO.setup(RoAPin, GPIO.IN)    # input mode
	GPIO.setup(RoBPin, GPIO.IN)
	GPIO.setup(RoSPin,GPIO.IN,pull_up_down=GPIO.PUD_UP)
	strip.begin()
	# strip.setBrightness(64)
	startupSequence()

objs = [
	{"gpioPin": 13, "startValue": 111, "maxspeed": 0.05},		# BAT
	{"gpioPin": 19, "startValue": 123, "maxspeed": 1.0 },		# MOUSE
	{"gpioPin": 26, "startValue": 134, "maxspeed": 0.5 },		# SQUIRREL
	{"gpioPin": 16, "startValue": 30, "maxspeed": 1.0 },		# ELEPHANT
	{"gpioPin": 20, "startValue": 23, "maxspeed": 0.5 },		# PEACOCK
	{"gpioPin": 21, "startValue": 1, "maxspeed": 0.0 }			# WHALE
]

class Audio:
	def __init__(self, id, gpio_pin, start_value, maxspeed):
		self.id = id
		self.button = Button(gpio_pin)
		self.start_value = start_value
		self.maxspeed = maxspeed

		self.button.when_pressed = self.pressed 

	def pressed(self):
		print("pressed")
		
		global maxspeed
		maxspeed = self.maxspeed

		clearLights()

		global globalCounter
		globalCounter = remapValues(self.start_value, 0, 135, 0, 1000)

		# setAudioClip(self.id)

audiobuttons = []

for index, item in enumerate(objs):
	ab = Audio(index, item["gpioPin"], item["startValue"], item["maxspeed"])
	audiobuttons.append(ab)

############################# ----- KNOB STUFF

def rotaryDeal():
    global flag
    global prev_pos
    global cur_pos
    global globalCounter

    prev_pos = GPIO.input(RoBPin)
    while(not GPIO.input(RoAPin)):
            cur_pos = GPIO.input(RoBPin)
            flag = 1
    if flag == 1:
        flag = 0
        if (prev_pos == 0) and (cur_pos == 1):
                globalCounter = globalCounter + 1
        if (prev_pos == 1) and (cur_pos == 0):
                globalCounter = globalCounter - 1
	   
	if globalCounter > max_counter:
		globalCounter = max_counter
	if globalCounter < 0:
		globalCounter = 0 

############################# ----- Main Loop

def loop():
	global globalCounter
	global value
	global prev_value
	global isIdle
	global timeOfLastAction

	while True:
		rotaryDeal()

		prev_value = value
		value = int(remapValues(globalCounter, 0, max_counter, 0, 135))

		if prev_value != value:
			if isIdle:
				clearLights()
				isIdle = False
			timeOfLastAction = time.time()
			calcValues(value)
		else:
			if isIdle:
				idleLights()
			else:
				checkTime(timeOfLastAction)

		# print str(isIdle) + " " + str(value)

if __name__ == '__main__':
	setup()
	try:
		loop()
	except KeyboardInterrupt:
		clearLights()
		GPIO.cleanup()

