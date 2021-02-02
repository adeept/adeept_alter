#!/usr/bin/env python3

import time
import RPi.GPIO as GPIO


GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

# Corresponding interface Motor A
Motor_EN    = 4
Motor_Pin1  = 26
Motor_Pin2  = 21

'''
Motor B interface corresponds to BCM pin numbers: EN 17, Pin1 27, Pin2 18
'''

GPIO.setup(Motor_EN, GPIO.OUT)
GPIO.setup(Motor_Pin1, GPIO.OUT)
GPIO.setup(Motor_Pin2, GPIO.OUT)

pwm_A = GPIO.PWM(Motor_EN, 1000)

if __name__ == '__main__':
	GPIO.output(Motor_Pin1, GPIO.HIGH)
	GPIO.output(Motor_Pin2, GPIO.LOW)
	pwm_A.start(100)

	pwm_A.ChangeDutyCycle(100)
	time.sleep(2)

	pwm_A.ChangeDutyCycle(20)
	time.sleep(2)

	#Switch between high and low levels to make the motor rotate in reverse
	GPIO.output(Motor_Pin1, GPIO.LOW)
	GPIO.output(Motor_Pin2, GPIO.HIGH)
	time.sleep(2)

	pwm_A.ChangeDutyCycle(100)
	time.sleep(2)

	GPIO.cleanup()
