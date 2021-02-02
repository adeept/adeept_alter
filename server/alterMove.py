#!/usr/bin/python3

import Adafruit_PCA9685
import numpy as np 
import time
import threading
import oledCtrl
import robotLight
import move as dc

dc.setup()
dc.motorStop()

from mpu6050 import mpu6050
import Kalman_filter

light = robotLight.RobotLight()
light.start()

pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(50)

'''
0 autoSelect
1 diagonalSelect
2 triangularSelect
'''
selectGait = 0
speedApart = 50

init_pwm0 = 348
init_pwm1 = 215
init_pwm2 = 360
init_pwm3 = 204

init_pwm4 = 255
init_pwm5 = 390
init_pwm6 = 240
init_pwm7 = 399

init_pwm8 = 300
init_pwm9 = 300
init_pwm10 = 300
init_pwm11 = 300

init_pwm12 = 300
init_pwm13 = 300
init_pwm14 = 300
init_pwm15 = 300

LA = 23.0
LB = 51.336
LC = 12.5

linkageDInput = [LA, LB]

initPos = [init_pwm0,init_pwm1,init_pwm2,init_pwm3,
		   init_pwm4,init_pwm5,init_pwm6,init_pwm7,
		   init_pwm8,init_pwm9,init_pwm10,init_pwm11,
		   init_pwm12,init_pwm13,init_pwm14,init_pwm15]

lastPos = [0,50, 0,50, 0,50, 0,50]
goalPos = [0,50, 0,50, 0,50, 0,50]
nowPos = [0,50, 0,50, 0,50, 0,50]

sc_direction = [1,-1,1,-1, -1,1,-1,1, 1,1,1,1, 1,1,1,1]
DPI = 1
delayTime = 0.01

ctrlRangeMax = 560
ctrlRangeMin = 100
angleRange = 205

walkWiggle = 30.0
walkHeight = 60.0
liftHeight = 6.0

walkOffset = 0.0
middleOffset = 0.0

maxHeight = 65.0
minHeight = 45.0
middleHeight = (maxHeight + minHeight)/2

offSetD = 0.0

sinput = 1

'''
------
0	4
1	5
  +
2	6
3	7
------
------
8	10
  +
9	11
------	
'''
MPU_connection = 0
try:
	sensor = mpu6050(0x68)
	MPU_connection = 1
	print('mpu6050 connected')
except:
	MPU_connection = 0
	print('mpu6050 disconnected')

kfX = Kalman_filter.Kalman_filter(0.01,0.1)
kfY = Kalman_filter.Kalman_filter(0.01,0.1)

def anGen(ani):
	return int(round(((ctrlRangeMax-ctrlRangeMin)/angleRange*ani),0))


def linkageD(linkageLen, servoNum, goalPosZ): #E
	sqrtGenOut = np.sqrt(goalPosZ[0]*goalPosZ[0]+goalPosZ[1]*goalPosZ[1])
	nGenOut = (linkageLen[0]*linkageLen[0]+goalPosZ[0]*goalPosZ[0]+goalPosZ[1]*goalPosZ[1]-linkageLen[1]*linkageLen[1])/(2*linkageLen[0]*sqrtGenOut)
	angleA = np.arccos(nGenOut)*180/np.pi

	AB = goalPosZ[1]/goalPosZ[0]

	angleB = np.arctan(AB)*180/np.pi
	angleGenA = angleB - angleA

	return angleGenA*sc_direction[servoNum]


def initServos():
	for i in range(0,16):
		pwm.set_pwm(i, 0, initPos[i])


def linkageQ(leg, x, y):
	x = -x
	x1 = x-LC/2
	x2 = -x1-LC/2

	if leg == 1:
		a = linkageD(linkageDInput, 0, [y,x1])
		b = linkageD(linkageDInput, 1, [y,x2])
		pwm.set_pwm(0,0,init_pwm0 + anGen(a))
		pwm.set_pwm(1,0,init_pwm1 + anGen(b))
	elif leg == 2:
		a = linkageD(linkageDInput, 2, [y,x1])
		b = linkageD(linkageDInput, 3, [y,x2])
		pwm.set_pwm(2,0,init_pwm2 + anGen(a))
		pwm.set_pwm(3,0,init_pwm3 + anGen(b))
	elif leg == 3:
		a = linkageD(linkageDInput, 4, [y,x1])
		b = linkageD(linkageDInput, 5, [y,x2])
		pwm.set_pwm(4,0,init_pwm4 + anGen(a))
		pwm.set_pwm(5,0,init_pwm5 + anGen(b))
	elif leg == 4:
		a = linkageD(linkageDInput, 6, [y,x1])
		b = linkageD(linkageDInput, 7, [y,x2])
		pwm.set_pwm(6,0,init_pwm6 + anGen(a))
		pwm.set_pwm(7,0,init_pwm7 + anGen(b))

	return a,b


def legStep(s, direc, offset, legName):
	liftD = 0
	if legName == 1 or legName == 3:
		if s == 7:
			liftD = offSetD
		elif s == 8:
			liftD = offSetD/2
		elif s == 9:
			liftD = offSetD/4

	elif legName == 2 or legName == 4:
		if s == 1:
			liftD = offSetD
		elif s == 2:
			liftD = offSetD/2
		elif s == 3:
			liftD == offSetD/4

	if s <= 10 and s > 0:
		x = (walkWiggle/2 - (walkWiggle/9)*(s-1))*direc + offset
		# y = walkHeight + (walkWiggle/2-x)*middleOffset/(walkWiggle/2) - liftD
		y = walkHeight - liftD
	elif s == 11:
		x = -walkWiggle/3*2*direc + offset
		y = walkHeight - liftHeight
	elif s == 12:
		x = walkWiggle/3*2*direc + offset
		y = walkHeight - liftHeight 
	elif s == -1:
		x = offset
		y = walkHeight - liftHeight 

	return x, y


def move(command):
	global sinput

	if command == 'forward':
		leftD  = 1
		rightD = 1
	elif command == 'backward':
		leftD  = -1
		rightD = -1
	elif command == 'left':
		leftD  = -1
		rightD = 1
	elif command == 'right':
		leftD  = 1
		rightD = -1

	if sinput == 1:
		goalPos[0],goalPos[1] = legStep(1,  leftD,   walkOffset, 1)
		goalPos[2],goalPos[3] = legStep(10, leftD,  -walkOffset, 2)
		goalPos[4],goalPos[5] = legStep(7,  rightD,  walkOffset, 3)
		goalPos[6],goalPos[7] = legStep(4,  rightD, -walkOffset, 4)
	elif sinput == 2:
		goalPos[0],goalPos[1] = legStep(2,  leftD,   walkOffset, 1)
		goalPos[2],goalPos[3] = legStep(11, leftD,  -walkOffset, 2)
		goalPos[4],goalPos[5] = legStep(8,  rightD,  walkOffset, 3)
		goalPos[6],goalPos[7] = legStep(5,  rightD, -walkOffset, 4)
	elif sinput == 3:
		goalPos[0],goalPos[1] = legStep(3,  leftD,   walkOffset, 1)
		goalPos[2],goalPos[3] = legStep(12, leftD,  -walkOffset, 2)
		goalPos[4],goalPos[5] = legStep(9,  rightD,  walkOffset, 3)
		goalPos[6],goalPos[7] = legStep(6,  rightD, -walkOffset, 4)
	elif sinput == 4:
		goalPos[0],goalPos[1] = legStep(4,  leftD,   walkOffset, 1)
		goalPos[2],goalPos[3] = legStep(1,  leftD,  -walkOffset, 2)
		goalPos[4],goalPos[5] = legStep(10, rightD,  walkOffset, 3)
		goalPos[6],goalPos[7] = legStep(7,  rightD, -walkOffset, 4)
	elif sinput == 5:
		goalPos[0],goalPos[1] = legStep(5,  leftD,   walkOffset, 1)
		goalPos[2],goalPos[3] = legStep(2,  leftD,  -walkOffset, 2)
		goalPos[4],goalPos[5] = legStep(11, rightD,  walkOffset, 3)
		goalPos[6],goalPos[7] = legStep(8,  rightD, -walkOffset, 4)
	elif sinput == 6:
		goalPos[0],goalPos[1] = legStep(6,  leftD,   walkOffset, 1)
		goalPos[2],goalPos[3] = legStep(3,  leftD,  -walkOffset, 2)
		goalPos[4],goalPos[5] = legStep(12, rightD,  walkOffset, 3)
		goalPos[6],goalPos[7] = legStep(9,  rightD, -walkOffset, 4)
	elif sinput == 7:
		goalPos[0],goalPos[1] = legStep(7,  leftD,   walkOffset, 1)
		goalPos[2],goalPos[3] = legStep(4,  leftD,  -walkOffset, 2)
		goalPos[4],goalPos[5] = legStep(1,  rightD,  walkOffset, 3)
		goalPos[6],goalPos[7] = legStep(10, rightD, -walkOffset, 4)
	elif sinput == 8:
		goalPos[0],goalPos[1] = legStep(8,  leftD,   walkOffset, 1)
		goalPos[2],goalPos[3] = legStep(5,  leftD,  -walkOffset, 2)
		goalPos[4],goalPos[5] = legStep(2,  rightD,  walkOffset, 3)
		goalPos[6],goalPos[7] = legStep(11, rightD, -walkOffset, 4)
	elif sinput == 9:
		goalPos[0],goalPos[1] = legStep(9,  leftD,   walkOffset, 1)
		goalPos[2],goalPos[3] = legStep(6,  leftD,  -walkOffset, 2)
		goalPos[4],goalPos[5] = legStep(3,  rightD,  walkOffset, 3)
		goalPos[6],goalPos[7] = legStep(12, rightD, -walkOffset, 4)
	elif sinput == 10:
		goalPos[0],goalPos[1] = legStep(10, leftD,   walkOffset, 1)
		goalPos[2],goalPos[3] = legStep(7,  leftD,  -walkOffset, 2)
		goalPos[4],goalPos[5] = legStep(4,  rightD,  walkOffset, 3)
		goalPos[6],goalPos[7] = legStep(1,  rightD, -walkOffset, 4)
	elif sinput == 11:
		goalPos[0],goalPos[1] = legStep(11, leftD,   walkOffset, 1)
		goalPos[2],goalPos[3] = legStep(8,  leftD,  -walkOffset, 2)
		goalPos[4],goalPos[5] = legStep(5,  rightD,  walkOffset, 3)
		goalPos[6],goalPos[7] = legStep(2,  rightD, -walkOffset, 4)
	elif sinput == 12:
		goalPos[0],goalPos[1] = legStep(12, leftD,   walkOffset, 1)
		goalPos[2],goalPos[3] = legStep(9,  leftD,  -walkOffset, 2)
		goalPos[4],goalPos[5] = legStep(6,  rightD,  walkOffset, 3)
		goalPos[6],goalPos[7] = legStep(3,  rightD, -walkOffset, 4)

	sinput += 1
	if sinput > 12:
		sinput = 1


def moveD(command):
	global sinput

	if command == 'forward':
		leftD  = 1
		rightD = 1
	elif command == 'backward':
		leftD  = -1
		rightD = -1
	elif command == 'left':
		leftD  = -1
		rightD = 1
	elif command == 'right':
		leftD  = 1
		rightD = -1
	else:
		return

	if sinput == 1:
		goalPos[0],goalPos[1] = legStep(1,  leftD,   walkOffset, -1)
		goalPos[2],goalPos[3] = legStep(7,  leftD,  -walkOffset, -1)
		goalPos[4],goalPos[5] = legStep(7,  rightD,  walkOffset, -1)
		goalPos[6],goalPos[7] = legStep(1,  rightD, -walkOffset, -1)
	elif sinput == 2:
		goalPos[0],goalPos[1] = legStep(2,  leftD,   walkOffset, -1)
		goalPos[2],goalPos[3] = legStep(8,  leftD,  -walkOffset, -1)
		goalPos[4],goalPos[5] = legStep(8,  rightD,  walkOffset, -1)
		goalPos[6],goalPos[7] = legStep(2,  rightD, -walkOffset, -1)
	elif sinput == 3:
		goalPos[0],goalPos[1] = legStep(3,  leftD,   walkOffset, -1)
		goalPos[2],goalPos[3] = legStep(9,  leftD,  -walkOffset, -1)
		goalPos[4],goalPos[5] = legStep(9,  rightD,  walkOffset, -1)
		goalPos[6],goalPos[7] = legStep(3,  rightD, -walkOffset, -1)
	elif sinput == 4:
		goalPos[0],goalPos[1] = legStep(4,  leftD,   walkOffset, -1)
		goalPos[2],goalPos[3] = legStep(10, leftD,  -walkOffset, -1)
		goalPos[4],goalPos[5] = legStep(10, rightD,  walkOffset, -1)
		goalPos[6],goalPos[7] = legStep(4,  rightD, -walkOffset, -1)
	elif sinput == 5:
		goalPos[0],goalPos[1] = legStep(5,  leftD,   walkOffset, -1)
		goalPos[2],goalPos[3] = legStep(11, leftD,  -walkOffset, -1)
		goalPos[4],goalPos[5] = legStep(11, rightD,  walkOffset, -1)
		goalPos[6],goalPos[7] = legStep(5,  rightD, -walkOffset, -1)
	elif sinput == 6:
		goalPos[0],goalPos[1] = legStep(6,  leftD,   walkOffset, -1)
		goalPos[2],goalPos[3] = legStep(12, leftD,  -walkOffset, -1)
		goalPos[4],goalPos[5] = legStep(12, rightD,  walkOffset, -1)
		goalPos[6],goalPos[7] = legStep(6,  rightD, -walkOffset, -1)
	elif sinput == 7:
		goalPos[0],goalPos[1] = legStep(7,  leftD,   walkOffset, -1)
		goalPos[2],goalPos[3] = legStep(1,  leftD,  -walkOffset, -1)
		goalPos[4],goalPos[5] = legStep(1,  rightD,  walkOffset, -1)
		goalPos[6],goalPos[7] = legStep(7,  rightD, -walkOffset, -1)
	elif sinput == 8:
		goalPos[0],goalPos[1] = legStep(8,  leftD,   walkOffset, -1)
		goalPos[2],goalPos[3] = legStep(2,  leftD,  -walkOffset, -1)
		goalPos[4],goalPos[5] = legStep(2,  rightD,  walkOffset, -1)
		goalPos[6],goalPos[7] = legStep(8,  rightD, -walkOffset, -1)
	elif sinput == 9:
		goalPos[0],goalPos[1] = legStep(9,  leftD,   walkOffset, -1)
		goalPos[2],goalPos[3] = legStep(3,  leftD,  -walkOffset, -1)
		goalPos[4],goalPos[5] = legStep(3,  rightD,  walkOffset, -1)
		goalPos[6],goalPos[7] = legStep(9,  rightD, -walkOffset, -1)
	elif sinput == 10:
		goalPos[0],goalPos[1] = legStep(10, leftD,   walkOffset, -1)
		goalPos[2],goalPos[3] = legStep(4,  leftD,  -walkOffset, -1)
		goalPos[4],goalPos[5] = legStep(4,  rightD,  walkOffset, -1)
		goalPos[6],goalPos[7] = legStep(10, rightD, -walkOffset, -1)
	elif sinput == 11:
		goalPos[0],goalPos[1] = legStep(11, leftD,   walkOffset, -1)
		goalPos[2],goalPos[3] = legStep(5,  leftD,  -walkOffset, -1)
		goalPos[4],goalPos[5] = legStep(5,  rightD,  walkOffset, -1)
		goalPos[6],goalPos[7] = legStep(11, rightD, -walkOffset, -1)
	elif sinput == 12:
		goalPos[0],goalPos[1] = legStep(12, leftD,   walkOffset, -1)
		goalPos[2],goalPos[3] = legStep(6,  leftD,  -walkOffset, -1)
		goalPos[4],goalPos[5] = legStep(6,  rightD,  walkOffset, -1)
		goalPos[6],goalPos[7] = legStep(12, rightD, -walkOffset, -1)

	sinput += 1
	if sinput > 12:
		sinput = 1


def rangeCtrl(minIn, maxIn, val):
	if val > maxIn:
		val = maxIn
	elif val < minIn:
		val = minIn
	return val


def pitchRoll(pIn, rIn):
	xIn = 0

	y_1 = rangeCtrl(minHeight, maxHeight, middleHeight + pIn - rIn)
	y_2 = rangeCtrl(minHeight, maxHeight, middleHeight - pIn - rIn)
	y_3 = rangeCtrl(minHeight, maxHeight, middleHeight + pIn + rIn)
	y_4 = rangeCtrl(minHeight, maxHeight, middleHeight - pIn + rIn)

	linkageQ(1, xIn, y_1)
	linkageQ(2, xIn, y_2)
	linkageQ(3, xIn, y_3)
	linkageQ(4, xIn, y_4)


def stay(hIn):
	hIn = rangeCtrl(minHeight, maxHeight, hIn)
	linkageQ(1, 0, hIn)
	linkageQ(2, 0, hIn)
	linkageQ(3, 0, hIn)
	linkageQ(4, 0, hIn)


# while 1:
# 	stay(60)
# 	time.sleep(2)
# 	stay(73)
# 	time.sleep(2)
	# for i in range(0,25):
	# 	stay(45+i)
	# 	time.sleep(delayTime)
	# for i in range(0,25):
	# 	stay(70-i)
	# 	time.sleep(delayTime)


def smove():
	for i in range(0,DPI+1):
		x_1 = lastPos[0] + ((goalPos[0]-lastPos[0])/DPI)*i
		y_1 = lastPos[1] + ((goalPos[1]-lastPos[1])/DPI)*i

		x_2 = lastPos[2] + ((goalPos[2]-lastPos[2])/DPI)*i
		y_2 = lastPos[3] + ((goalPos[3]-lastPos[3])/DPI)*i

		x_3 = lastPos[4] + ((goalPos[4]-lastPos[4])/DPI)*i
		y_3 = lastPos[5] + ((goalPos[5]-lastPos[5])/DPI)*i

		x_4 = lastPos[6] + ((goalPos[6]-lastPos[6])/DPI)*i
		y_4 = lastPos[7] + ((goalPos[7]-lastPos[7])/DPI)*i

		linkageQ(1, x_1, y_1)
		linkageQ(2, x_2, y_2)
		linkageQ(3, x_3, y_3)
		linkageQ(4, x_4, y_4)

		time.sleep(delayTime)

	for i in range(0,8):
		lastPos[i] = goalPos[i]


'''
Lights Ctrl Functions
'''
def set2812(Rinput, Ginput, Binput):
	light.setColor(Rinput, Ginput, Binput)


def setSome2812(Rinput, Ginput, Binput, idArray):
	light.setSomeColor(Rinput, Ginput, Binput, idArray)


def startPoliceLight():
	light.police()


def startBreathLight(Rinput, Ginput, Binput):
	light.breath(Rinput, Ginput, Binput)


def frontLightCtrl(command):
	'''
	command: 'on' 'off'
	'''
	light.frontLight(command)


def lightStop():
	light.pause()


'''
Ports Ctrl functions
'''
def switchCtrl(portNum, command):
	'''
	portNum: 1 2 3
	command: 0 1
	'''
	light.switch(portNum, command)


def allPortsLow():
	light.set_all_switch_off()



class Alter(threading.Thread):

	def __init__(self, *args, **kwargs):
		super(Alter, self).__init__(*args, **kwargs)
		self.__flag = threading.Event()
		self.__flag.clear()
		self.moveDirection = 'no'
		self.turnDirection = 'no'
		self.commandInput  = 'no'
		self.moveSpeed     = 100

		self.accSpeed   = 1
		self.initSpeed  = 300
		self.deltaSpeed = 20

		self.funcMode  = 'no'
		self.classicLastCommand = 'no'

		self.xMiddle = 1.38
		self.yMiddle = 0

		self.mpuDelay= 0.05

		self.pitchValue = 0
		self.rollValue  = 0
		self.initPitch  = 0
		self.initRoll   = 0
		self.valueP     = 0.7


	def pause(self):
		print('......................pause..........................')
		self.__flag.clear()


	def resume(self):
		print('resume')
		self.__flag.set()


	def steadyProcessing(self):
		global MPU_connection, sensor
		if MPU_connection:
			try:
				valueGet = sensor.get_accel_data()
			except:
				try:
					sensor = mpu6050(0x68)
					MPU_connection = 1
					print('mpu6050 connected')
				except:
					MPU_connection = 0
					print('mpu6050 disconnected')
		else:
			return
		xGet = kfX.kalman(valueGet['x'])
		yGet = kfY.kalman(valueGet['y'])

		xDebug = xGet - self.xMiddle
		yDebug = yGet - self.yMiddle

		self.pitchValue = rangeCtrl((minHeight - middleHeight), (maxHeight - middleHeight), self.pitchValue + xDebug*self.valueP)
		self.rollValue  = rangeCtrl((minHeight - middleHeight), (maxHeight - middleHeight), self.rollValue - yDebug*self.valueP)
		# print('debug:', xDebug)
		# print('pitch:', self.pitchValue)
		try:
			pitchRoll(self.pitchValue, self.rollValue)
		except:
			pass

		time.sleep(self.mpuDelay)


	def moveAlter(self, speed, direction, turning, rInput):
		print('direction:', direction)
		print('turning:', turning)
		self.moveSpeed = speed
		self.moveDirection = direction
		self.turnDirection = turning
		self.funcMode = 'no'
		if self.turnDirection != 'no':
			self.commandInput = self.turnDirection
		elif self.turnDirection == 'no' and self.moveDirection != 'no':
			self.commandInput = self.moveDirection
		elif self.turnDirection == 'no' and self.moveDirection == 'no':
			self.commandInput = 'no'
			self.moveStop()
			return
		self.resume()


	def moveStop(self):
		self.pause()
		self.moveDirection = 'no'
		self.turnDirection = 'no'
		self.funcMode = 'no'
		self.speedNow = 300
		self.deltaSpeed = 20
		self.pitchValue = self.initPitch
		self.rollValue  = self.initRoll
		stay(walkHeight)

		pwm.set_pwm(8, 0, self.initSpeed)
		pwm.set_pwm(9, 0, self.initSpeed)
		pwm.set_pwm(10, 0, self.initSpeed)
		pwm.set_pwm(11, 0, self.initSpeed)

		dc.motorStop()


	def classicMove(self, command):
		if command == 'no':
			self.moveStop()
			return

		maxDeltaSpeed = self.moveSpeed * 2
		if self.deltaSpeed < maxDeltaSpeed:
			self.deltaSpeed += self.accSpeed
		else:
			self.deltaSpeed = maxDeltaSpeed

		if command == 'forward':
			pwm.set_pwm(8, 0, self.initSpeed + self.deltaSpeed)
			pwm.set_pwm(9, 0, self.initSpeed + self.deltaSpeed)
			pwm.set_pwm(10, 0, self.initSpeed- self.deltaSpeed)
			pwm.set_pwm(11, 0, self.initSpeed- self.deltaSpeed)

		elif command == 'backward':
			pwm.set_pwm(8, 0, self.initSpeed - self.deltaSpeed)
			pwm.set_pwm(9, 0, self.initSpeed - self.deltaSpeed)
			pwm.set_pwm(10, 0, self.initSpeed+ self.deltaSpeed)
			pwm.set_pwm(11, 0, self.initSpeed+ self.deltaSpeed)

		elif command == 'left':
			pwm.set_pwm(8, 0, self.initSpeed - self.deltaSpeed)
			pwm.set_pwm(9, 0, self.initSpeed - self.deltaSpeed)
			pwm.set_pwm(10, 0, self.initSpeed- self.deltaSpeed)
			pwm.set_pwm(11, 0, self.initSpeed- self.deltaSpeed)

		elif command == 'right':
			pwm.set_pwm(8, 0, self.initSpeed - self.deltaSpeed)
			pwm.set_pwm(9, 0, self.initSpeed - self.deltaSpeed)
			pwm.set_pwm(10, 0, self.initSpeed- self.deltaSpeed)
			pwm.set_pwm(11, 0, self.initSpeed- self.deltaSpeed)

		self.classicLastCommand = command


	def racingMove(self, command):
		pass


	def functionSelect(self, funcName):
		self.funcMode = funcName
		self.resume()


	def alterThread(self):
		if selectGait == 0:
			if self.moveSpeed < speedApart:
				move(self.commandInput)
				smove()
			elif self.moveSpeed > speedApart:
				moveD(self.commandInput)
				smove()
		elif selectGait == 1:
			moveD(self.commandInput)
			smove()
		elif selectGait == 2:
			move(self.commandInput)
			smove()

		self.classicMove(self.commandInput)
		dc.move(100, self.moveDirection, self.turnDirection, 1)


	def funcProcessing(self):
		if self.funcMode == 'steady':
			self.steadyProcessing()


	def run(self):
		while 1:
			self.__flag.wait()
			if self.funcMode == 'no':
				self.alterThread()
				if self.moveDirection == 'no' and self.turnDirection =='no':
					self.moveStop()
					stay(walkHeight)

			else:
				self.funcProcessing()
				if self.funcMode == 'no':
					stay(walkHeight)
					continue
			print('moveThreading')
			pass



class OLED(threading.Thread):

	def __init__(self, *args, **kwargs):
		super(OLED, self).__init__(*args, **kwargs)
		self.__flag = threading.Event()
		self.__flag.clear()
		self.lookCommand = 'no'

	def pause(self):
		print('......................pause..........................')
		self.__flag.clear()

	def resume(self):
		print('resume')
		self.__flag.set()

	def showLooks(self, command):
		'''
		command:laugh locked fell concentrate normal
		'''
		self.lookCommand = command
		self.resume()

	def oledShowText(self, textInput, x, y):
		oledCtrl.showText(textInput, x, y)

	def oledThread(self):
		oledCtrl.looksCtrl(self.lookCommand)
		self.pause()

	def run(self):
		while 1:
			self.__flag.wait()
			self.oledThread()
			print('oledThreading')
			pass



# pitchRoll(15, 15)

'''
alter = Alter()
alter.start()

alter.functionSelect('steady')
'''

'''
time.sleep(30)

alter.moveAlter(100, 'forward', 'no', 0)

time.sleep(3)

alter.moveStop()
'''

'''
screen = OLED()
screen.start()

startBreathLight(92, 128, 255)

screen.oledShowText('SBD', 0, 0)
frontLightCtrl('on')

alter.moveAlter(100, 'forward', 'no', 0)
time.sleep(3)
alter.moveStop()

# screen.showLooks('laugh')
lightStop()
set2812(35,35,35)
time.sleep(1)
frontLightCtrl('off')

alter.moveAlter(100, 'backward', 'left', 0)
time.sleep(3)
alter.moveStop()

startPoliceLight()
time.sleep(1)

alter.moveAlter(40, 'backward', 'no', 0)
time.sleep(3)
alter.moveStop()

set2812(0,0,0)
time.sleep(1)
# screen.showLooks('laugh')
alter.moveAlter(40, 'forward', 'no', 0)
time.sleep(2)
alter.moveStop()

lightStop()
'''

# while 1:
# 	linkageQ(1, walkWiggle/2, walkHeight)
# 	time.sleep(1)
# 	linkageQ(1, -walkWiggle/2, walkHeight)
# 	time.sleep(1)
# 	linkageQ(1, 0, walkHeight-liftHeight)
# 	time.sleep(1)
# 	pass

# initServos()

# while 1:
# 	moveD('forward')
# 	smove()
	# print('loop')
	# pass

# while 1:
# 	forDPI()
# 	pass

# while 1:
# 	for i in range(0,20):
# 		linkageQ(2,(-10),65-i)
# 		linkageQ(1,(25),65-i)

# 		time.sleep(0.02)

# 	for i in range(0,20):
# 		linkageQ(2,(-10),45+i)
# 		linkageQ(1,(25),45+i)

# 		time.sleep(0.02)


# while 1:
# 	for i in range(0,20):
# 		linkageQ(2,(25),65-i)
# 		linkageQ(1,(25),65-i)
# 		linkageQ(3,(25),65-i)
# 		linkageQ(4,(25),65-i)
# 		time.sleep(0.02)

# 	for i in range(0,20):
# 		linkageQ(2,(25),45+i)
# 		linkageQ(1,(25),45+i)
# 		linkageQ(3,(25),45+i)
# 		linkageQ(4,(25),45+i)
# 		time.sleep(0.02)


# while 1:
# 	for i in range(0,60):
# 		a = linkageD(linkageDInput, 1, [60,30-i])
# 		pwm.set_pwm(1,0,init_pwm1 + anGen(a))
# 		time.sleep(0.02)

# while 1:
# 	for i in range(0,60):
# 		a = linkageD(linkageDInput, 0, [60,-30+i])
# 		pwm.set_pwm(0,0,init_pwm0 + anGen(a))
# 		time.sleep(0.01)

# a = anGen(90)
# b = anGen(0)

# while 1:
# 	pwm.set_pwm(0,0,init_pwm0 + a)
# 	print(a)
# 	time.sleep(1)
# 	pwm.set_pwm(0,0,init_pwm0 + b)
# 	print(b)
# 	time.sleep(1)