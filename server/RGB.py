#!/usr/bin/python3
# File name   : Ultrasonic.py
# Description : Detection distance and tracking with ultrasonic
# Website     : www.gewbot.com
# Author      : William
# Date        : 2019/02/23
import RPi.GPIO as GPIO
import time


Tx = 11
Rx = 8

def checkdist():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(Tx, GPIO.OUT)
    GPIO.setup(Rx, GPIO.OUT)
    
    GPIO.output(Tx, GPIO.LOW)
    GPIO.output(Rx, GPIO.HIGH)
    
    GPIO.setup(Rx, GPIO.IN)
    while  GPIO.input(Rx):
        pass
    t1 = time.time()

    while not GPIO.input(Rx):
        pass
    t2 = time.time()
    GPIO.setup(Tx, GPIO.OUT)
    GPIO.output(Tx, GPIO.HIGH)
    
    return round((t2-t1)*340/2,2)


def setColor(R, G, B):
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(Tx, GPIO.OUT)
    GPIO.setup(Rx, GPIO.OUT)
    GPIO.output(Rx, GPIO.LOW)
    GPIO.output(Tx, GPIO.HIGH)
    
    if R:
        GPIO.output(Rx, GPIO.HIGH)
    else:
        GPIO.output(Rx, GPIO.LOW)

    GPIO.output(Tx, GPIO.LOW)
    GPIO.output(Tx, GPIO.HIGH)

    if G:
        GPIO.output(Rx, GPIO.HIGH)
    else:
        GPIO.output(Rx, GPIO.LOW)

    GPIO.output(Tx, GPIO.LOW)
    GPIO.output(Tx, GPIO.HIGH)

    if B:
        GPIO.output(Rx, GPIO.HIGH)
    else:
        GPIO.output(Rx, GPIO.LOW)

    GPIO.output(Tx, GPIO.LOW)
    GPIO.output(Tx, GPIO.HIGH)
    
    GPIO.output(Tx, GPIO.HIGH)
    GPIO.output(Rx, GPIO.HIGH)


if __name__ == '__main__':
    while 1:
        setColor(1,0,0)
        time.sleep(1)
        setColor(0,1,0)
        time.sleep(1)
        setColor(0,0,1)
        time.sleep(1)

        a = checkdist()
        print(a)

        time.sleep(0.1)