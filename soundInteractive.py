import os
import math
import time
from gpiozero import Button, LED
from gpiozero import MCP3008
import RPi.GPIO as GPIO
from dotstar import Adafruit_DotStar

# - - - setup pixels

numpixels = 45
strip   = Adafruit_DotStar(numpixels)

# - - - setup rotary encoder

RoAPin = 17	# pin11
RoBPin = 18	# pin12
RoSPin = 27	# pin13

globalCounter = 0	# master counter for rotary encoder value

flag = 0
prev_pos = 0
cur_pos = 0
prev_counter = 0

max_counter = 1000	# maximum counting value for the rot encoder
#if this is bigger, you have to turn the knob more to make the light move

############################# ----- Setup variables

value = 0				# value that remaps all other variables   		goes from 0-135
prev_value = 0

volume = 0.0
maxspeed = 1
minspeed = 0
whichLED = 0

idleTime = 5		# how long the thing will wait before starting to idle (in seconds)
brightnessIdleTime = 10000		#this number determines how fast/slow the brightness loop happens during idle


#################################################################################################### Send messages to PD

def send2Pd(message=''):
	os.system("echo '" + message + "' | pdsend 3333")	# this value must match receive value in the pd file
	# print "send to PD " + message

def setAudioClip(num):		# these functions generate the messages that get send in the first function
	# 0 = bat 1 = bird		# the first number is the route, used in pd to parse where the message is sent
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

#################################################################################################### Calculating values to send

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
	elif val >= 90 and val <= 110:
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

	prevLED = whichLED
	whichLED = int(remapValues(val, 0, 135, 0, numpixels - 1))	

	if (prevLED != whichLED):
		strip.setPixelColor(prevLED, 0)
		strip.setPixelColor(whichLED, 0xFF0000)
		strip.show()
	else:
		strip.setPixelColor(whichLED, 0xFF0000)
		strip.show()

def calcValues(val):
	# print ("current value: " + str(val))

	calcPlaybackSpeed(val)
	calcVolume(val)
	setLED(val)

############################# ----- Setup time interaction

def clearLights():			# turning off all lights
	for led in range(numpixels):
		strip.setBrightness(64)
		strip.setPixelColor(led, 0)
	strip.show()

# color = 0x0000FF
# idleled = 0

idleCounter = 0

def idleLights(counter):		#make brightness go up and down during idle

	for led in range(numpixels):
		strip.setPixelColor(led, 0xFF0000)

	if counter <= 5000:
		strip.setBrightness(int(remapValues(counter, 0, brightnessIdleTime/2, 0, 60)))
	else:
		strip.setBrightness(int(remapValues(counter, brightnessIdleTime/2, brightnessIdleTime, 60, 0)))
	strip.show()

	if currLED != None:
		currLED.off()

timeOfLastAction = 0
isIdle = False

def checkTime(actionTime):		#check if there's any action, if not then idle
	# print("elapsed time: " + str(time.time() - buttonTime))
	if time.time() - actionTime > idleTime:
		global isIdle
		isIdle = True
		setVolume(0)

def startupSequence():			# red/yellow/green light show on boot
	colors = [0x009900, 0x999900, 0x990000, 0]
	for color in colors:
		for led in range(numpixels):
			strip.setPixelColor(led, color)
			strip.show()
			time.sleep(0.3 / 50)


############################# ----- Setup Buttoms

def setup():
	GPIO.setup(RoAPin, GPIO.IN)
	GPIO.setup(RoBPin, GPIO.IN)
	GPIO.setup(RoSPin,GPIO.IN,pull_up_down=GPIO.PUD_UP)
	strip.begin()
	strip.setBrightness(64)
	startupSequence()

# startvalue is an estimate of where in the untra/infra sound spectrum the audio clip would hypothetically be
# based on actual frequency of call, i guesstimated these values.
# 0-45 is low frequency, 45-90 is human audible frequency, 90-135 is high frequency

# maxspeed is generated from the default playback value from audiotester.pd
# if it's .1+ -> max speed is 1, if it's .01-.09 -> maxspeed is 0.5. these values also just kind of guesstimated based on how the audio sounded when I sped it up 
# and where it started to smush together to the point where you can't get anything out of it

	
objs = [			#values for maxspeed can be adjusted based on how things sound, should it be playing faster at the high end of the range? 
	{"buttonPin": 22, "ledPin": 13, "startValue": 123, "maxspeed": 0.1},		# BAT
	{"buttonPin": 23, "ledPin": 19, "startValue": 134, "maxspeed": 1.3 },		# MOUSE
	{"buttonPin": 24, "ledPin": 26, "startValue": 111, "maxspeed": 0.8 },		# SQUIRREL
	{"buttonPin": 5, "ledPin": 16, "startValue": 15, "maxspeed": 1.3 },			# ELEPHANT
	{"buttonPin": 6, "ledPin": 20, "startValue": 5, "maxspeed": 0.8 },			# PEACOCK
	{"buttonPin": 12, "ledPin": 21, "startValue": 17, "maxspeed": 1.5 }			# WHALE
]

currLED = None

class Audio:
	def __init__(self, id, button_pin, led_pin, start_value, maxspeed):
		self.id = id
		self.button = Button(button_pin)
		self.led = LED(led_pin)
		self.start_value = start_value
		self.maxspeed = maxspeed

		self.button.when_pressed = self.pressed 

	def pressed(self):
		# print("pressed")
		
		global maxspeed
		maxspeed = self.maxspeed

		global currLED
		if currLED != None:
			currLED.off()
		currLED = self.led

		currLED.on()

		clearLights()

		global globalCounter
		globalCounter = remapValues(self.start_value, 0, 135, 0, 1000)

		setAudioClip(self.id)
		
		setVolume(0)
		setLED(globalCounter)

audiobuttons = []

for index, item in enumerate(objs):
	ab = Audio(index, item["buttonPin"], item["ledPin"], item["startValue"], item["maxspeed"])
	audiobuttons.append(ab)

############################# ----- KNOB STUFF

def rotaryDeal():
	global flag
	global prev_pos
	global cur_pos
	global globalCounter

	starttime = time.time()

	prev_pos = GPIO.input(RoBPin)
	while(not GPIO.input(RoAPin)):
			cur_pos = GPIO.input(RoBPin)
			flag = 1
			if time.time() - starttime > 0.5:		#breaking out of the loop if it's stuck
				break 								#hack solution
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


#################################################################################################### Main Loop

def loop():
	global globalCounter
	global value
	global prev_value
	global isIdle
	global timeOfLastAction
	global idleCounter

	while True:
		rotaryDeal()		#function to check value of rotary encoder

		prev_value = value 		#checking the current value against previous value
		value = int(remapValues(globalCounter, 0, max_counter, 0, 135))

		if prev_value != value:		# if it's different, then it's active
			if isIdle:
				clearLights()
				currLED.on()
				isIdle = False
			timeOfLastAction = time.time()
			calcValues(value)
		else:						# if it's the same, figure out if it's idling or not.
			if isIdle:
				idleCounter +=1
				if idleCounter > brightnessIdleTime:		# if this number is bigger, the idle brightness will loop slower
					idleCounter = 0
				idleLights(idleCounter)
			else:
				checkTime(timeOfLastAction)

if __name__ == '__main__':
	setup()
	try:
		loop()
	except KeyboardInterrupt:
		clearLights()
		GPIO.cleanup()

