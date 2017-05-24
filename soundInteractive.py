import os
import math
import time
from gpiozero import Button
from gpiozero import MCP3008

import RPi.GPIO as GPIO

RoAPin = 17    # pin11
RoBPin = 18    # pin12
RoSPin = 27    # pin13

globalCounter = 0

flag = 0
Last_RoB_Status = 0
Current_RoB_Status = 0
prev_Counter = 0

#################################################################################################### Setup variables

value = 0				# VALUE that maps value for all other variables   		0-135

volume = 0.0
maxspeed = 1
minspeed = 0
whichLED = 0

#################################################################################################### Send messages to PD

def send2Pd(message=''):
	os.system("echo '" + message + "' | pdsend 3333")
	print "send to PD " + message

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
	return round(outValue, 5)

def calcPlaybackSpeed(val):
	if val < 45:
		global currentspeed
		currentspeed = 0
	elif val >= 45 and val < 100:
		global currentspeed
		currentspeed = remapValues(val, 45, 100, 0, maxspeed)
	else: 
		global currentspeed
		currentspeed = maxspeed

	setPlaybackSpeed(currentspeed)
	print("currentspeed: " + str(currentspeed))
	# setPlaybackSpeed(currentspeed)

def calcVolume(val):
	if val < 25 or val > 110:
		global volume
		volume = 0
	elif val >= 25 and val < 45:
		global volume
		volume = remapValues(val, 25, 45, 0.1, 1.0)
	elif val >= 90 and val < 110:
		global volume
		volume = remapValues(val, 90, 110, 1.0, 0.1)
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

#################################################################################################### Setup time interaction

doCheckTime = False
button_time = 0

def checkTime(buttonTime):
	# print("elapsed time: " + str(time.time() - buttonTime))
	if time.time() - buttonTime > 15:
		global doCheckTime
		doCheckTime = False
		pause()
	

#################################################################################################### Setup Buttoms

button_pause = Button(12)

def setup():
	# GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
	GPIO.setup(RoAPin, GPIO.IN)    # input mode
	GPIO.setup(RoBPin, GPIO.IN)
	GPIO.setup(RoSPin,GPIO.IN,pull_up_down=GPIO.PUD_UP)
	rotaryClear()

objs = [
	{"gpioPin": 13, "startValue": 111, "maxspeed": 0.05},		# BAT
	{"gpioPin": 19, "startValue": 123, "maxspeed": 1.0 },		# MOUSE
	{"gpioPin": 26, "startValue": 134, "maxspeed": 0.5 },		# SQUIRREL
	{"gpioPin": 16, "startValue": 30, "maxspeed": 1.0 },		# ELEPHANT
	{"gpioPin": 20, "startValue": 23, "maxspeed": 0.5 },		# PEACOCK
	{"gpioPin": 21, "startValue": 0, "maxspeed": 0.0 }		# WHALE <<< NOT IN PD YET
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

		global button_time
		button_time = time.time()

		global doCheckTime
		doCheckTime = True
		
		global current_audio
		current_audio = self.id
		
		global maxspeed
		maxspeed = self.maxspeed

		global value
		value = self.start_value

		calcValues(value)
		audioSwitcher(self.id)

audiobuttons = []

for index, item in enumerate(objs):
	ab = Audio(index, item["gpioPin"], item["startValue"], item["maxspeed"])
	audiobuttons.append(ab)

#################################################################################################### KNOB STUFF

def knobTurned(counter):
	global prev_Counter
	global value
	global button_time
	global doCheckTime

	if counter > prev_Counter:
		print "turn up"
		value = value + 1
		if value > 135:
			value = 135
		button_time = time.time()
		doCheckTime = True
		calcValues(value)
	else:
		print "turn down"
		value = value - 1
		if value < 0:
			value = 0
		button_time = time.time()
		doCheckTime = True
		calcValues(value)

	prev_Counter = counter

def rotaryDeal():
	global flag
	global Last_RoB_Status
	global Current_RoB_Status
	global globalCounter
	Last_RoB_Status = GPIO.input(RoBPin)
	while(not GPIO.input(RoAPin)):
		Current_RoB_Status = GPIO.input(RoBPin)
		flag = 1
	if flag == 1:
		flag = 0
		if (Last_RoB_Status == 0) and (Current_RoB_Status == 1):
			globalCounter = globalCounter + 1
			# print 'globalCounter = %d' % globalCounter
		if (Last_RoB_Status == 1) and (Current_RoB_Status == 0):
			globalCounter = globalCounter - 1
			# print 'globalCounter = %d' % globalCounter

		if globalCounter%100 == 0:

			knobTurned(globalCounter)

def clear(ev=None):
        globalCounter = 0
	print 'globalCounter = %d' % globalCounter
	time.sleep(1)

def rotaryClear():
        GPIO.add_event_detect(RoSPin, GPIO.FALLING, callback=clear) # wait for falling

def destroy():
	GPIO.cleanup()             # Release resourcesS

#################################################################################################### Main Loop

def loop():
	global globalCounter
	global doCheckTime
	global value

	while True:
		rotaryDeal()
		if (button_pause.is_pressed):
			pause()

		if doCheckTime:
			checkTime(button_time)

if __name__ == '__main__':     # Program start from here
	setup()
	try:
		loop()
	except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
		destroy()

