'''
Import apds9960 related libraries
'''
import smbus2
from apds9960.const import *
from apds9960 import APDS9960

'''
I2C communication of apds9960, if the line is not connected or the connection is wrong, 
an error will be reported at this step
'''
port = 1
address = 0x39
bus = smbus2.SMBus(port)

'''
Object instantiation
'''
apds = APDS9960(bus)
apds.setProximityIntLowThreshold(50)

'''
Start reading gesture information
'''
print("Gesture Test")
apds.enableGestureSensor()
while 1:
	if apds.isGestureAvailable():
		motion = apds.readGesture()
		print(motion)
	'''
	There are about 5 return values of apds.readGesture()
	Including from left to right, right to left, top to bottom, bottom to top, near to far
	Use the numbers 1 2 3 4 5 instead. Which number corresponds to which gesture depends on your sensor placement
	'''
	pass