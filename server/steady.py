'''
This program needs to be run in the server folder
'''
import alterMove
import time

'''
Import MPU6050 library
'''
from mpu6050 import mpu6050

'''
Import Kaman filter library
'''
import Kalman_filter

'''
Instantiate MPU6050 object, the default I2C address is 0x68
'''
sensor = mpu6050(0x68)
print('mpu6050 connected')

'''
Instantiate the Kalman filter object on the XY axis, the Kalman filter can make the value read from the sensor smoother
'''
kfX = Kalman_filter.Kalman_filter(0.01,0.1)
kfY = Kalman_filter.Kalman_filter(0.01,0.1)

'''
Set the maximum height and minimum height
And find the middle height through the maximum height and the minimum height
When the robot is on a horizontal plane, each leg of the robot is in the middle height state
The maximum and minimum height is used to limit the range of movement of the robot's legs
'''
maxHeight = 65.0
minHeight = 45.0
middleHeight = (maxHeight + minHeight)/2

'''
Since the automatic balance mode needs to continuously read information from the MPU6050
Read the information once, calculate the change trend once, and apply the new angle to the steering gear. This series of actions is called a cycle
So use this variable here to set the time interval between every two loops
'''
mpuDelay = 0.05

'''
If the robot pitches up and down to a certain angle when placed on a horizontal plane, modify xMiddle
If the robot is tilted at a certain angle left and right when placed on a horizontal plane, modify yMiddle
This can also be used in reverse. For example, when you want the robot to maintain a certain angle, you can adjust these two variables.
'''
xMiddle  = 1.3
yMiddle  = 0

'''
P value in simple PID controller, proportional parameter, increase this value if the robot moves slowly
If the robot is not stable and shakes too much, reduce this value
'''
valueP   = 0.7

'''
Because this control method is closed loop control
So save the accumulated error (error) in these two variables
This allows the robot to stay level at any time even if it is on a constantly shaking panel
'''
pitchValue = 0
rollValue  = 0


'''
This function is used to limit the size of a variable
Enter the maximum and minimum values, enter the variables that need to be limited
The return value is between the maximum and minimum values (including the maximum and minimum values)
'''
def rangeCtrl(minIn, maxIn, val):
	if val > maxIn:
		val = maxIn
	elif val < minIn:
		val = minIn
	return val


'''
This function is used to adjust the angle of the robot:
pitch is pitch movement
roll is rolling motion
pIn is used to adjust the movement of the pitch axis, the larger the value of pIn, the more the robot will raise its head
rIn is used to adjust the movement of the roll axis, the larger the rIn value, the more the robot tilts to the left
'''
def pitchRoll(pIn, rIn):
	'''
	Because the back and forth movement of the legs is not required in the automatic stabilization mode
	So the X-axis coordinate point of the end point of each leg is 0
	'''
	xIn = 0

	'''
	Calculate the Y value of the end point of each leg through pIn and rIn
	'''
	y_1 = rangeCtrl(minHeight, maxHeight, middleHeight + pIn - rIn)
	y_2 = rangeCtrl(minHeight, maxHeight, middleHeight - pIn - rIn)
	y_3 = rangeCtrl(minHeight, maxHeight, middleHeight + pIn + rIn)
	y_4 = rangeCtrl(minHeight, maxHeight, middleHeight - pIn + rIn)

	'''
	Apply new coordinate values to the four legs
	'''
	alterMove.linkageQ(1, xIn, y_1)
	alterMove.linkageQ(2, xIn, y_2)
	alterMove.linkageQ(3, xIn, y_3)
	alterMove.linkageQ(4, xIn, y_4)


'''
This function is a function of the self-stabilization function
Call it cyclically to realize the self-stabilization function
'''
def steadyProcessing():
	'''
	Declared as a global variable
	'''
	global pitchValue, rollValue, sensor

	'''
	If the I2C communication is disconnected, re-instantiate the MPU6050 object
	'''
	try:
		valueGet = sensor.get_accel_data()
		print(valueGet)
	except:
		sensor = mpu6050(0x68)
		print('mpu6050 connected')

	'''
	Obtain the X-axis and Y-axis readings of MPU6050, use Kalman filter to eliminate the noise of MPU6050 readings
	'''
	xGet = kfX.kalman(valueGet['x'])
	yGet = kfY.kalman(valueGet['y'])

	'''
	Calculate the deviation value of each axis
	'''
	xDebug = xGet - xMiddle
	yDebug = yGet - yMiddle

	'''
	Calculate pitchValue and rollValue based on the deviation value, and apply the result to pitchRoll()
	'''
	pitchValue = rangeCtrl((minHeight - middleHeight), (maxHeight - middleHeight), pitchValue + xDebug*valueP)
	rollValue  = rangeCtrl((minHeight - middleHeight), (maxHeight - middleHeight), rollValue - yDebug*valueP)
	pitchRoll(pitchValue, rollValue)

	'''
	Delay for a while before proceeding to the next cycle
	'''
	time.sleep(mpuDelay)


if __name__ == '__main__':
	while True:
		steadyProcessing()