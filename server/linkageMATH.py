#!/usr/bin/python3
'''
Import the library used to control the steering gear
'''
import Adafruit_PCA9685
import time

'''
Import math function library
'''
import numpy as np 

'''
Instantiate the library used to control the steering gear
'''
pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(50)


'''
The PWM value of the corresponding servo when the arm of the servo is vertically downward
Here only the front left leg of DOG is taken as an example
The corresponding PWM port numbers of the two servos on the left front leg are 0 and 1 respectively
The specific values of the two variables here are different for each robot
'''
init_pwm0 = 348
init_pwm1 = 215

'''
This array is used to adjust the swing direction of each servo
'''
sc_direction = [1,-1]

'''
LA is the length of the first joint of the link
LB is the length of the second joint of the link
LC is the distance between the two servo axes in a leg
'''
LA = 23.0
LB = 51.336
LC = 12.5

linkageDInput = [LA, LB]

'''
Parameters related to steering gear angle control
ctrlRangeMax is the maximum effective PWM of the steering gear
ctrlRangeMin is the smallest effective PWM of the steering gear
angleRange is the actual rotation range of the steering gear
'''
ctrlRangeMax = 560
ctrlRangeMin = 100
angleRange = 205

'''
This function enters the angle to return the PWM value
'''
def anGen(ani):
	return int(round(((ctrlRangeMax-ctrlRangeMin)/angleRange*ani),0))


'''
This function passes in the length parameters of the two connecting rods of the leg, the servo number and the coordinate point
The return value is the angle that the servo needs to swing
'''
def linkageD(linkageLen, servoNum, goalPosZ):
	'''
	Here the mathematical principle can refer to Figure A in the document
	'''
	sqrtGenOut = np.sqrt(goalPosZ[0]*goalPosZ[0]+goalPosZ[1]*goalPosZ[1])
	nGenOut = (linkageLen[0]*linkageLen[0]+goalPosZ[0]*goalPosZ[0]+goalPosZ[1]*goalPosZ[1]-linkageLen[1]*linkageLen[1])/(2*linkageLen[0]*sqrtGenOut)
	angleA = np.arccos(nGenOut)*180/np.pi

	AB = goalPosZ[1]/goalPosZ[0]

	angleB = np.arctan(AB)*180/np.pi
	angleGenA = angleB - angleA

	'''
	By multiplying the returned angle by
	'''
	return angleGenA*sc_direction[servoNum]


'''
This function passes in the coordinate point, controls the movement of the point at the end of the leg to the coordinate point, and returns the angle of the two servos at the same time
'''
def linkageQ(x, y):
	'''
	The mathematical principle here can refer to Figure B in the document
	'''
	x = -x
	x1 = x-LC/2
	x2 = -x1-LC/2

	a = linkageD(linkageDInput, 0, [y,x1])
	b = linkageD(linkageDInput, 1, [y,x2])
	pwm.set_pwm(0,0,init_pwm0 + anGen(a))
	pwm.set_pwm(1,0,init_pwm1 + anGen(b))

	return a,b


if __name__ == '__main__':
	while True:
		linkageQ(15, 60)
		time.sleep(1)
		linkageQ(-15, 60)
		time.sleep(2)