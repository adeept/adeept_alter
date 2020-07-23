import Adafruit_PCA9685
import time

pwm = Adafruit_PCA9685.PCA9685()
pwm.set_pwm_freq(50)

pwm.set_pwm(8, 0, 330)
pwm.set_pwm(9, 0, 330)
pwm.set_pwm(10, 0, 330)
pwm.set_pwm(11, 0, 330)

time.sleep(3)
for i in range(0,100):
	pwm.set_pwm(11, 0, 300+i)
	print(300+i)
	time.sleep(0.1)