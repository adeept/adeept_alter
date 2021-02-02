import RPi.GPIO as GPIO
import time
import alterMove
'''
Import and instantiate the object used to control Alter
'''
alter = alterMove.Alter()
alter.start()

'''
Set the GPIO pin number of the three-way tracking module
'''
line_pin_right = 19
line_pin_middle = 16
line_pin_left = 20

'''
Set the speed during line tracking
'''
moveSpeed = 100


'''
Initialize GPIO
'''
def setup():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(line_pin_right,GPIO.IN)
    GPIO.setup(line_pin_middle,GPIO.IN)
    GPIO.setup(line_pin_left,GPIO.IN)


'''
Main function
'''
def run():
    while 1:
        '''
        Get the values of the three sensors of the tracking module
        '''
        status_left = GPIO.input(line_pin_right)
        status_middle = GPIO.input(line_pin_middle)
        status_right = GPIO.input(line_pin_left)

        '''
        Turn off the three lights of ws2812
        '''
        alterMove.setSome2812(0, 0, 0, [0, 1, 2])

        '''
        Determine which light of WS2812 is on according to the sensor value of the tracking module. 
        If the light needs to be kept off, let the fourth light be on (Alter does not have a fourth light, so it is off)
        '''
        '''
        Use the status of the light to observe whether the robot can detect the line correctly. If the line cannot be detected correctly, 
        you need to use a screwdriver to adjust the potentiometer on the tracking module.
        '''
        if status_left:
            leftStu = 0
        else:
            leftStu = 3

        if status_middle:
            middleStu = 1
        else:
            middleStu = 3

        if status_right:
            rightStu = 2
        else:
            rightStu = 3
        
        '''
        Turn on the corresponding light according to the sensor value of the tracking module. If the left and right are reversed, switch the positions of leftStu and rightStu
        '''
        alterMove.setSome2812(255, 64, 128, [rightStu, middleStu, leftStu])

        
        '''
        If the three sensors of the tracking module detect the black line for a period of time or the robot is picked up for a period of time, it stops moving
        '''
        if status_middle == 1 and status_left == 1 and status_right == 1:
            timeCut = 0
            while  GPIO.input(line_pin_right) and GPIO.input(line_pin_middle) and GPIO.input(line_pin_left):
                timeCut += 1
                time.sleep(0.01)
                if timeCut >= 50:
                    alter.moveStop()
                pass

        elif status_middle == 1:
            alter.moveAlter(moveSpeed, 'forward', 'no', 1)
        elif status_left == 1:
            alter.moveAlter(moveSpeed, 'no', 'left', 0.3)
        elif status_right == 1:
            alter.moveAlter(moveSpeed, 'no', 'right', 0.3)
        elif status_middle == 0 and status_left == 0 and status_right == 0:
            alter.moveAlter(moveSpeed, 'backward', 'no', 1)



if __name__ == '__main__':
    try:
        setup()
        while 1:
            run()
        pass
    except KeyboardInterrupt:
        alter.moveStop()