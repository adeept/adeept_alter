import Adafruit_PCA9685		#Import the library that controls the steering gear
import time

pwm = Adafruit_PCA9685.PCA9685()	 # Instantiate the steering gear control object
pwm.set_pwm_freq(50)	# Set the PWM frequency of the servo (frequency is not duty cycle)

ctrlPort   = 8
startMoveA = 339	# The bigger one
startMoveB = 314	# The smaller of the two numbers noted in the previous step
'''
Add those two numbers and divide by two, take the middle value as the PWM that controls the steering gear 
to stop rotating, int() is used to convert the result to an integer
'''
stopPWM = int((startMoveA+startMoveB)/2)


'''
The parameter direction import 1 and -1 to control the direction of rotation, import 0 to stop the rotation
The parameter speed import speed size, if not imported, the default value is 0
'''
def ctrlServo(direction, speed=0):
	if direction == -1:
		setPWM = startMoveA - speed
	elif direction == 1:
		setPWM = startMoveB + speed
	elif direction == 0:
		setPWM = stopPWM

	pwm.set_pwm(ctrlPort, 0, setPWM)

# Import parameters according to position, the first is direction, the second is speed
ctrlServo(-1, 100)
time.sleep(2)
# Import according to the parameter name, the position relationship can be free
ctrlServo(speed = 50, direction = 1)
time.sleep(2)
# If the speed parameter is not imported, speed is the default value
ctrlServo(0)