import Adafruit_PCA9685

pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(50)

initPWM  = 320
setPWM   = initPWM
ctrlPort = 11

def main():
	global setPWM
	while 1:
		commandInput = input()
		if commandInput == 'w':
			setPWM += 1
		elif commandInput == 's':
			setPWM -= 1

		pwm.set_pwm(ctrlPort, 0, setPWM)
		print(setPWM)


try:
	main()
except KeyboardInterrupt:
	pwm.set_pwm(ctrlPort, 0, initPWM)