import Adafruit_PCA9685
import time
import threading

pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(50)


class Alter(threading.Thread):
	def __init__(self, *args, **kwargs):
		super(Alter, self).__init__(*args, **kwargs)
		self.__flag = threading.Event()
		self.__flag.clear()

		self.commandInput = 'no'
		self.moveSpeed     = 100
		self.deltaSpeed = 0
		self.accSpeed = 1

		self.speedStopMin_08 = 314
		self.speedStopMin_09 = 315
		self.speedStopMin_10 = 314
		self.speedStopMin_11 = 316

		self.speedStopMax_08 = 339
		self.speedStopMax_09 = 341
		self.speedStopMax_10 = 339
		self.speedStopMax_11 = 342

		self.speedStop_08 = int((self.speedStopMin_08+self.speedStopMax_08)/2)
		self.speedStop_09 = int((self.speedStopMin_09+self.speedStopMax_09)/2)
		self.speedStop_10 = int((self.speedStopMin_10+self.speedStopMax_10)/2)
		self.speedStop_11 = int((self.speedStopMin_11+self.speedStopMax_11)/2)


	def pause(self):
		self.__flag.clear()


	def resume(self):
		self.__flag.set()


	def moveAlter(self, speed, command):
		self.moveSpeed = speed
		self.commandInput = command
		if self.commandInput == 'no':
			self.moveStop()
			return
		self.resume()


	def moveStop(self):
		self.pause()
		self.commandInput = 'no'
		self.deltaSpeed = 0
		pwm.set_pwm(8,  0, self.speedStop_08)
		pwm.set_pwm(9,  0, self.speedStop_09)
		pwm.set_pwm(10, 0, self.speedStop_10)
		pwm.set_pwm(11, 0, self.speedStop_11)


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
			pwm.set_pwm(8,  0, self.speedStopMax_08 + self.deltaSpeed)
			pwm.set_pwm(9,  0, self.speedStopMax_09 + self.deltaSpeed)
			pwm.set_pwm(10, 0, self.speedStopMin_10 - self.deltaSpeed)
			pwm.set_pwm(11, 0, self.speedStopMin_11 - self.deltaSpeed)

		elif command == 'backward':
			pwm.set_pwm(8,  0, self.speedStopMin_08 - self.deltaSpeed)
			pwm.set_pwm(9,  0, self.speedStopMin_09 - self.deltaSpeed)
			pwm.set_pwm(10, 0, self.speedStopMax_10 + self.deltaSpeed)
			pwm.set_pwm(11, 0, self.speedStopMax_11 + self.deltaSpeed)

		elif command == 'left':
			pwm.set_pwm(8,  0, self.speedStopMin_08 - self.deltaSpeed)
			pwm.set_pwm(9,  0, self.speedStopMin_09 - self.deltaSpeed)
			pwm.set_pwm(10, 0, self.speedStopMin_10 - self.deltaSpeed)
			pwm.set_pwm(11, 0, self.speedStopMin_11 - self.deltaSpeed)

		elif command == 'right':
			pwm.set_pwm(8,  0, self.speedStopMax_08 + self.deltaSpeed)
			pwm.set_pwm(9,  0, self.speedStopMax_09 + self.deltaSpeed)
			pwm.set_pwm(10, 0, self.speedStopMax_10 + self.deltaSpeed)
			pwm.set_pwm(11, 0, self.speedStopMax_11 + self.deltaSpeed)

		self.classicLastCommand = command

		time.sleep(0.02)


	def run(self):
		while 1:
			self.__flag.wait()
			self.classicMove(self.commandInput)


if __name__ == '__main__':
	alter = Alter()
	alter.start()
	alter.moveAlter(100, 'forward')
	time.sleep(5)
	alter.moveStop()
	alter.moveAlter(100, 'right')
	time.sleep(5)
	alter.moveStop()
	alter.moveAlter(100, 'left')
	time.sleep(5)
	alter.moveStop()
	alter.moveAlter(100, 'backward')
	time.sleep(5)
	alter.moveStop()