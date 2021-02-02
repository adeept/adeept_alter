'''
This program needs to be run in the server folder
When the robot falls to the ground, the robot's legs will swing
'''
import alterMove
import time

'''
Import random function library
'''
import random

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
Since only Y-axis readings need to be detected, only one Kalman filter object needs to be instantiated here
'''
kfY = Kalman_filter.Kalman_filter(0.01,0.1)

'''
Height when the robot is standing
'''
stayHeight = 55

'''
Set the swing range of the robot's legs
'''
wiggleRange = 10

'''
Use this variable here to set the time interval between every two loops
'''
mpuDelay = 0.1

'''
Set the threshold for judging whether the robot is down
'''
failValue = 6

'''
After detecting that the robot is righted, execute this function to control the robot to stand steady
'''
def standStill():
	alterMove.linkageQ(1, 0, stayHeight)
	alterMove.linkageQ(2, 0, stayHeight)
	alterMove.linkageQ(3, 0, stayHeight)
	alterMove.linkageQ(4, 0, stayHeight)


'''
After detecting that the robot is down, execute this function to control the robot's legs to swing randomly
'''
def wiggle():
	'''
	Use randint() to generate integers from -wiggleRange to wiggleRange
	'''
	alterMove.linkageQ(1, 0, stayHeight + random.randint(-wiggleRange,wiggleRange))
	alterMove.linkageQ(2, 0, stayHeight + random.randint(-wiggleRange,wiggleRange))
	alterMove.linkageQ(3, 0, stayHeight + random.randint(-wiggleRange,wiggleRange))
	alterMove.linkageQ(4, 0, stayHeight + random.randint(-wiggleRange,wiggleRange))


if __name__ == '__main__':
	while True:
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
		Obtain the Y-axis readings of MPU6050, use Kalman filter to eliminate the noise of MPU6050 readings
		'''
		yGet = kfY.kalman(valueGet['y'])

		'''
		If the Y-axis reading is greater than the absolute value of the threshold used to judge whether the robot is down, swing the leg
		Otherwise stand still
		'''
		if abs(yGet) > failValue:
			wiggle()
		else:
			standStill()

		'''
		Delay for a while before proceeding to the next cycle
		'''
		time.sleep(mpuDelay)

