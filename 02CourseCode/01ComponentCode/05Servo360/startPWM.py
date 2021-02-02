import Adafruit_PCA9685	#Import the library that controls the steering gear

pwm = Adafruit_PCA9685.PCA9685()	# Instantiate the steering gear control object
pwm.set_pwm_freq(50)	# Set the PWM frequency of the servo (frequency is not duty cycle)
'''
First define an initial PWM value casually, after ctrl+c exits the operation, 
the PWM value of the corresponding interface will be set back to this initial value
'''
initPWM  = 320
setPWM   = initPWM	# This variable needs to be changed during program execution
ctrlPort = 8	#Which PWM port the servo is connected to, fill in which number, fill in 8 here to connect the servo to PWM port 8

# Define a main function to perform specific operations
def main():
	'''
	Since this value is defined outside the function and belongs to a global variable, it needs to be declared as a global variable before changing the global variable in the function
	'''
	global setPWM
	while 1:
		commandInput = input()
		if commandInput == 'w':	# Obtain keyboard commands
			setPWM += 1		# PWM value plus 1
		elif commandInput == 's':	# If the input is ‘s’
			setPWM -= 1		 # PWM value minus 1

		pwm.set_pwm(ctrlPort, 0, setPWM)	# Set the PWM value of the ctrl servo port to the new PWM value
		print(setPWM)	# Print out the newly set PWM value in the terminal

'''
If ctrl+c exits the operation, the servo port is set to initPWM
'''
try:
	main()
except KeyboardInterrupt:
	pwm.set_pwm(ctrlPort, 0, initPWM)