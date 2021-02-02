#!/usr/bin/env python3

import time
import RPi.GPIO as GPIO
import Adafruit_PCA9685
import alterMove
'''
Import and instantiate the object used to control Alter
'''
alter = alterMove.Alter()
alter.start()


Tr = 11 		# Ultrasonic module input terminal pin number
Ec = 8 			# Ultrasonic module output pin number

'''
The example in this tutorial is a normal blue ultrasonic module
Initialize the GPIO of the ultrasonic module
'''
GPIO.setmode(GPIO.BCM)
GPIO.setup(Tr, GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(Ec, GPIO.IN)


'''
When the ranging result is less than this value, turn to
'''
turnRange = 0.2

'''
Calling this function will get the return value of ranging
'''
def checkdist():
	GPIO.output(Tr, GPIO.HIGH) # Set the input terminal of the module to high level and send out an initial sound wave
	time.sleep(0.000015)
	GPIO.output(Tr, GPIO.LOW)

	while not GPIO.input(Ec): # When the module no longer receives the initial sound wave
		pass
	t1 = time.time() # Note the time when the initial sound wave was emitted
	while GPIO.input(Ec): # When the module receives the return sound wave
		pass
	t2 = time.time() # Note the time when the return sound wave was captured

	return round((t2-t1)*340/2,2) # Calculate distance


print('Turn on automatic obstacle avoidance mode')
distDect = None

while 1:
	distDect = checkdist()
	print(distDect) # Print out the distance measurement results

	'''
	If the measured distance ahead is less than the value specified by turnRang, turn left; otherwise, go forward
	'''
	if distDect < turnRange:
		alter.moveAlter(100, 'no', 'left', 0.3)
	else:
		alter.moveAlter(100, 'forward', 'no', 1)