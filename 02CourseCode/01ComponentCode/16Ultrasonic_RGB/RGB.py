'''
Import libraries used to control GPIO and time-related libraries
'''
import RPi.GPIO as GPIO
import time

'''
Define the GPIO pin number related to RGB ultrasonic
'''
Tx = 11
Rx = 8

'''
Call this function to return distance information
'''
def checkdist():
    '''
    GPIO pin initialization, due to the different functions of GPIO pins when ultrasonic ranging and controlling the color of RGB lights
    Therefore, it needs to be initialized according to the specific function before using the relevant function
    '''
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(Tx, GPIO.OUT)
    GPIO.setup(Rx, GPIO.OUT)
    
    '''
    Control RGB ultrasonic to enter the ranging mode
    '''
    GPIO.output(Tx, GPIO.LOW)
    GPIO.output(Rx, GPIO.HIGH)
    
    '''
    Detect when the level of the Rx pin goes low, it means that the ultrasonic wave has been sent out, get time t1
    '''
    GPIO.setup(Rx, GPIO.IN)
    while  GPIO.input(Rx):
        pass
    t1 = time.time()

    '''
    Detect the duration of the low level of the Rx pin, and obtain the time t2 when the Rx pin becomes high
    '''
    while not GPIO.input(Rx):
        pass
    t2 = time.time()

    '''
    Control the RGB ultrasonic module to exit the ranging mode
    '''
    GPIO.setup(Tx, GPIO.OUT)
    GPIO.output(Tx, GPIO.HIGH)
    
    '''
    According to t1 and t2 and the speed of sound in the air, calculate the distance and return the value
    '''
    return round((t2-t1)*340/2,2)


'''
Call this function to change the color of the light on the RGB ultrasonic, divided into three channels of red, green and blue, each channel has two states (0 and 1)
R = 1, G = 0, B = 0 —— red
R = 0, G = 1, B = 0 —— green
R = 0, G = 0, B = 1 —— blue

R = 0, G = 0, B = 0 —— Go out
R = 1, G = 1, B = 1 —— All bright (close to white)
'''
def setColor(R, G, B):
    '''
    GPIO pin initialization
    '''
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(Tx, GPIO.OUT)
    GPIO.setup(Rx, GPIO.OUT)

    '''
    Enter the mode of changing color for the first time to set the R channel state
    '''
    GPIO.output(Rx, GPIO.LOW)
    GPIO.output(Tx, GPIO.HIGH)
    
    if R:
        GPIO.output(Rx, GPIO.HIGH)
    else:
        GPIO.output(Rx, GPIO.LOW)

    '''
    Enter the color changing mode for the second time to set the G channel state
    '''
    GPIO.output(Tx, GPIO.LOW)
    GPIO.output(Tx, GPIO.HIGH)

    if G:
        GPIO.output(Rx, GPIO.HIGH)
    else:
        GPIO.output(Rx, GPIO.LOW)

    '''
    Enter the mode of changing the color for the third time to set the state of the B channel
    '''
    GPIO.output(Tx, GPIO.LOW)
    GPIO.output(Tx, GPIO.HIGH)

    if B:
        GPIO.output(Rx, GPIO.HIGH)
    else:
        GPIO.output(Rx, GPIO.LOW)

    '''
    Exit to change color
    '''
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