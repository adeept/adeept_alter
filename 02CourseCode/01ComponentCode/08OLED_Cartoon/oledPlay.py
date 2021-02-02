#!/usr/bin/python3

import time

#Import OLED screen related libraries
import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

#Import libraries for image processing
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import os

#Obtain the absolute path of this file
curpath = os.path.realpath(__file__)
thisPath = "/" + os.path.dirname(curpath) + "/"

#OLED screen initialization
RST = 24
disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)
disp.begin()

#Set playback frame rate
FPS = 30

#Calculate the delay time per frame according to the playback frame rate
timeDelay = 1/FPS

#Clear the screen
disp.clear()
disp.display()

#All images will be stored in this array
LaughImage = []

#Set the folder where the ppm sequence string to be played comes from
ppmPath = 'ppm/'

#Get the names of all frames in this folder
ppmNames = os.listdir(ppmPath)

#Sort these files by name
ppmNames.sort()

#Import these frames
for frameName in ppmNames:
	#Open the file in PPM format and binarize it with convert('1')
	image = Image.open(thisPath+ppmPath+frameName).convert('1')
	#Store the converted image into LaughImage
	LaughImage.append(image)


#Displaying frame by frame is equivalent to playing a cartoon
for i in range(0, len(LaughImage)):
	disp.image(LaughImage[i])
	disp.display()
	time.sleep(timeDelay)