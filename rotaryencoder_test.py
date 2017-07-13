#!/usr/bin/env python
import RPi.GPIO as GPIO
import time
from dotstar import Adafruit_DotStar

numpixels = 45
datapin   = 23
clockpin  = 24
strip     = Adafruit_DotStar(numpixels, datapin, clockpin)

RoAPin = 11    # pin11
RoBPin = 12    # pin12
RoSPin = 13    # pin13

globalCounter = 0

flag = 0
prev_pos = 0
cur_pos = 0
prev_counter = 0

max_counter = 1000

def setup():
        GPIO.setmode(GPIO.BOARD)       # Numbers GPIOs by physical location
        GPIO.setup(RoAPin, GPIO.IN)    # input mode
        GPIO.setup(RoBPin, GPIO.IN)
        GPIO.setup(RoSPin,GPIO.IN,pull_up_down=GPIO.PUD_UP)
        rotaryClear()

        strip.begin()
        strip.setBrightness(64)

# def knobTurned(counter):
#         global prev_counter

#         if counter%100 == 0:
#                 if counter > prev_counter:
# #                       print "turn up"
#                         setLED(True)
#                 else:
# #                       print "turn down"
#                         setLED(False)

# #       print counter
#         prev_counter = counter

def remapValues(inValue, inMin, inMax, outMin, outMax):
    outValue = (((inValue - inMin) * (outMax - outMin)) / (inMax - inMin)) + outMin
    return int(outValue)

whichLED = 1
prevLED = 2
def setLED(counter):
        global whichLED
        global prevLED

        # for led in range(numpixels):
        strip.setPixelColor(prevLED, 0)

        prevLED = whichLED
        whichLED = remapValues(counter, 0, max_counter, 0, numpixels - 1)
        
        # print whichLED

        strip.setPixelColor(whichLED, 0x00FF00)
        strip.show()

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
        #       print 'globalCounter = %d' % globalCounter

        if (prev_pos == 1) and (cur_pos == 0):
                globalCounter = globalCounter - 1
        #       print 'globalCounter = %d' % globalCounter
                #print globalCounter

    if globalCounter > max_counter:
        globalCounter = max_counter
    if globalCounter < 0:
        globalCounter = 0           

    print globalCounter

    setLED(globalCounter)

def clear(ev=None):
   globalCounter = 0
#  print 'globalCounter = %d' % globalCounter
#  time.sleep(1)

def rotaryClear():
    GPIO.add_event_detect(RoSPin, GPIO.FALLING, callback=clear) # wait for falling

def loop():
    while True:
        rotaryDeal()

def destroy():
    GPIO.cleanup()             # Release resource

if __name__ == '__main__':     # Program start from here
        setup()
        try:
            loop()
        except KeyboardInterrupt:  # When 'Ctrl+C' is pressed, the child program destroy() will be  executed.
            destroy()