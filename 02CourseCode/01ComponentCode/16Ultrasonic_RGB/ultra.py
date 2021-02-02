#!/usr/bin/python3
# File name   : Ultrasonic.py
# Description : Detection distance and tracking with ultrasonic
# Website     : www.gewbot.com
# Author      : William
# Date        : 2019/02/23
import RPi.GPIO as GPIO
import time

Tr = 11
Ec = 8

Tx = 11
Rx = 8

RGBultrasonic = 0

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(Tr, GPIO.OUT,initial=GPIO.LOW)
GPIO.setup(Ec, GPIO.IN)


def setColor(R, G, B):
    if RGBultrasonic:
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


def checkdist():       #Reading distance
    if RGBultrasonic:
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

    else:
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(Tr, GPIO.OUT,initial=GPIO.LOW)
        GPIO.setup(Ec, GPIO.IN)
        GPIO.output(Tr, GPIO.HIGH)
        time.sleep(0.000015)
        GPIO.output(Tr, GPIO.LOW)
        while not GPIO.input(Ec):
            pass
        t1 = time.time()
        while GPIO.input(Ec):
            pass
        t2 = time.time()
        return round((t2-t1)*340/2,2)


if __name__ == '__main__':
    while 1:
        print(checkdist())
        time.sleep(1)
