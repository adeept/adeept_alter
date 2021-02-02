import RPi.GPIO as GPIO
import time

GPIO.setwarnings(False)		# There will be a warning when GPIO is defined repeatedly, ignore the warning
GPIO.setmode(GPIO.BCM)		# Set to BCM encoding encoding method
GPIO.setup(5, GPIO.OUT)		# The BCM number of the GPIO pin corresponding to the Port1 interface is 5
GPIO.setup(6, GPIO.OUT)		# The BCM number of the GPIO pin corresponding to the Port1 interface is 6
GPIO.setup(13, GPIO.OUT)	# The BCM number of the GPIO pin corresponding to the Port1 interface is 13

GPIO.output(5, GPIO.HIGH)	#Open Port1 interface
GPIO.output(6, GPIO.HIGH)	#Open Port2 interface
GPIO.output(13, GPIO.HIGH)	#Enable Port3 interface

time.sleep(3)	#Delay 3s

GPIO.output(5,GPIO.LOW)	#Close Port1 interface
GPIO.output(6,GPIO.LOW)	#Close Port2 interface
GPIO.output(13,GPIO.LOW)	#Close Port3 interface