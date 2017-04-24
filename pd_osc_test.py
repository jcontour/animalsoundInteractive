import os
from gpiozero import Button
from gpiozero import MCP3008

pot = MCP3008(channel=0)

def send2Pd(message=''):
	os.system("echo '" + message + "' | pdsend 3333")

def audioSwitcher(num):
	# 0 = bat 1 = bird
	message = '0 ' + str(num) + ';'
	print message
	# send2Pd(message)

def setPlaybackSpeed(val):
	message = '1 ' + str(val) + ';'
	print message
	# send2Pd(message)

objs = [
	{"buttonPin": 2, "pdArrayNum": 0, "startSpeed": 0.011, "increment": 0.01}
	{"buttonPin": 3, "pdArrayNum": 1, "startSpeed": 0.386, "increment": 0.1}
]

class Audio(obj):
	def __init__(self, id, button_pin, pd_array_num, start_speed, increment):
		self.id = id
		self.button_pin = button_pin
		self.button = Button(button_pin)
		self.start_speed = start_speed

		self.button.when_pressed = self.pressed 

		def pressed(self):
			global current_audio
				if (current_audio) == self.id:
					return
				print("pressed")
				audioSwitcher(self.id)
				setPlaybackSpeed(self.start_speed)

			current_audio = self.id
			print("current audio " + str(current_audio))

audiobuttons = []

for index, item in enumerate(objs):
	ab = Audio(index, item["buttonPin"], item["pdArrayNum"], item["startSpeed"], item["increment"])
	audiobuttons.append(ab)


#################### Main Loop

while (True):
	if (True): 
		print ("running")
		
pause()