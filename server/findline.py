#!/usr/bin/python3
# File name   : findline.py
# Description : line tracking 
# Website     : www.gewbot.com
# Author      : William
# Date        : 2019/08/28
import RPi.GPIO as GPIO
import time
import move
import alterMove

alter = alterMove.Alter()
alter.start()

line_pin_right = 19
line_pin_middle = 16
line_pin_left = 20

moveSpeed = 100

def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(line_pin_right,GPIO.IN)
    GPIO.setup(line_pin_middle,GPIO.IN)
    GPIO.setup(line_pin_left,GPIO.IN)
    #motor.setup()

def run():
    lastCommand = ''
    nowCommand  = ''
    while 1:
        # alter.moveAlter(moveSpeed, 'forward', 'no', 1)
        # time.sleep(10)

        # alter.moveAlter(moveSpeed, 'backward', 'no', 1)
        # time.sleep(10)
        
        status_right = GPIO.input(line_pin_right)
        status_middle = GPIO.input(line_pin_middle)
        status_left = GPIO.input(line_pin_left)
        # print('R%d   M%d   L%d'%(status_right,status_middle,status_left))
        '''
        if status_right and not status_middle and not status_left:
            screen.oledShowText('+'%(status_right,status_middle,status_left), 0, 0)

        elif status_right and status_middle and not status_left:
            screen.oledShowText('+'%(status_right,status_middle,status_left), 0, 0)
        '''
        alterMove.setSome2812(0, 0, 0, [0, 1, 2])

        if status_left:
            leftStu = 0
        else:
            leftStu = 3

        if status_middle:
            middleStu = 1
        else:
            middleStu = 4

        if status_right:
            rightStu = 2
        else:
            rightStu = 5
        

        alterMove.setSome2812(255, 64, 128, [leftStu, middleStu, rightStu])
        '''
        alter.moveAlter(moveSpeed, 'no', 'left', 0.3)
        time.sleep(1.5)
        alter.moveStop()
		'''
        
        if status_middle == 1 and status_left == 1 and status_right == 1:
            timeCut = 0
            while  GPIO.input(line_pin_right) and GPIO.input(line_pin_middle) and GPIO.input(line_pin_left):
                timeCut += 1
                time.sleep(0.01)
                if timeCut >= 50:
                    alter.moveStop()
                pass
            # alter.moveStop()
        elif status_middle == 1:
            alter.moveAlter(moveSpeed, 'forward', 'no', 1)
            nowCommand = 'forward'
        elif status_left == 1:
            alter.moveAlter(moveSpeed, 'no', 'right', 0.3)
            nowCommand = 'right'
        elif status_right == 1:
            alter.moveAlter(moveSpeed, 'no', 'left', 0.3)
            nowCommand == 'left'
        elif status_middle == 0 and status_left == 0 and status_right == 0:
            alter.moveAlter(moveSpeed, 'backward', 'no', 1)
            nowCommand = 'backward'
        
        

        
        
        


if __name__ == '__main__':
    try:
        setup()
        while 1:
            run()
        pass
    except KeyboardInterrupt:
        alter.moveStop()
