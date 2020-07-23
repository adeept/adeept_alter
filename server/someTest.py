import Adafruit_PCA9685

pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(50)

pausM_8 = 320  # min 315 # max 338
pausM_9 = 320  # min 317 # max 340
pausM_10= 320  # min 315 # max 338
pausM_11= 320  # min 318 # max 341

now_8 = pausM_8
now_9 = pausM_9
now_10= pausM_10
now_11= pausM_11

def main():
	global now_8, now_9, now_10, now_11
	while 1:
		sInput = input('command:')
		if sInput == 'w':
			now_11 += 1
		elif sInput == 's':
			now_11 -= 1
		pwm.set_pwm(11, 0, now_11)
		print(now_11)

if __name__ == '__main__':
	try:
		main()
	except:
		pwm.set_pwm(11, 0, pausM_11)