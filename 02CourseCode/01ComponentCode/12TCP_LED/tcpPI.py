'''
These two libraries are used to control WS2812 LED lights
'''
from rpi_ws281x import *
import argparse

'''
Import the socket library used for TCP communication
'''
import socket

'''
Some LED light settings are from the WS281X example
Source Code:https://github.com/rpi-ws281x/rpi-ws281x-python/
'''
LED_COUNT		= 24
LED_PIN			= 18
LED_FREQ_HZ		= 800000
LED_DMA			= 10
LED_BRIGHTNESS	= 255
LED_INVERT		= False
LED_CHANNEL		= 0

'''
Process arguments
'''
parser = argparse.ArgumentParser()
parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
args = parser.parse_args()

'''
Create NeoPixel object with appropriate configuration.
'''
strip = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)

'''
Intialize the library
'''
strip.begin()

'''
Next is the configuration related to TCP communication, where PORT is the defined port number, you can freely choose from 0-65535, it is recommended to choose the number after 1023, 
which needs to be consistent with the port number defined by the client in the PC
'''
HOST = ''
PORT = 10223
BUFSIZ = 1024
ADDR = (HOST, PORT)

tcpSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpSerSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
tcpSerSock.bind(ADDR)
tcpSerSock.listen(5)

'''
Start to monitor the client connection, after the client connection is successful, 
start to receive information sent from the client
'''
tcpCliSock, addr = tcpSerSock.accept()

while True:
    data = ''
    
    '''
    Receive information from the client
    '''
    '''
    Turn on the light if the message content is on
    If the message content is off, turn off the light
    '''
    data = str(tcpCliSock.recv(BUFSIZ).decode())
    if not data:
        continue

    elif 'on' == data:
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(255, 0, 255))
            strip.show()
            
    elif 'off' == data:
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(0, 0, 0))
            strip.show()
    
    '''
  Finally print out the received data, and start to monitor the next message sent by the client
    '''
    print(data)