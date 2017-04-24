import os
from gpiozero import Button
from gpiozero import MCP3008

pot = MCP3008(channel=0)

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

objs = [
	{"buttonPin": 2, "startSpeed": 0.011, "increment": 0.01},
	{"buttonPin": 3, "startSpeed": 0.386, "increment": 0.1}
]

class Audio:
	def __init__(self, id, button_pin, start_speed, increment):
		self.id = id
		self.button_pin = button_pin
		self.button = Button(button_pin)
		self.start_speed = start_speed
		self.increment = increment

		self.button.when_pressed = self.pressed 

	def pressed(self):
		print("pressed")
		
		#set global values
		global current_audio
		current_audio = self.id
		global increment
		increment = self.increment

		# audioSwitcher(self.id)

audiobuttons = []

for index, item in enumerate(objs):
	ab = Audio(index, item["buttonPin"], item["startSpeed"], item["increment"])
	audiobuttons.append(ab)

#################### Startup
audioSwitcher(0)
increment = audiobuttons[0].increment
current_audio = 0

#################### Main Loop

while (True):
	# IF it's been a while since input, stop playing audio?

	# when button pushed, change audio if selection is not current playing
	
	# wait for input from knob, when turned, add/subtract current increment value*degrees turned from current playSpeed

	# 

	print str(current_audio)
	print increment
	# print audiobuttons[current_audio].increment
	# currentspeed = pot.value*audiobuttons[current_audio].increment
	# setPlaybackSpeed(currentspeed)
		
pause()