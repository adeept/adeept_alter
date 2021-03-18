#!/usr/bin/python3

import time

import Adafruit_GPIO.SPI as SPI
import Adafruit_SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

import os

curpath = os.path.realpath(__file__)
thisPath = "/" + os.path.dirname(curpath)

# RST = 24
RST = None
FPS = 30
timeDelay = 1/FPS
imagesNum = 40

disp = Adafruit_SSD1306.SSD1306_128_64(rst=RST)
disp.begin()

disp.clear()
disp.display()

LaughImage = []

for i in range(0, imagesNum):
	image = Image.open('%s/faceImage/laugh/laugh%d.ppm'%(thisPath,i)).convert('1')
	LaughImage.append(image)

width = disp.width
height = disp.height
image = Image.new('1', (width, height))

draw = ImageDraw.Draw(image)

def showLook(lookSequence):
	for i in range(0, len(lookSequence), 2):
		disp.image(lookSequence[i])
		disp.display()
		time.sleep(timeDelay)


def looksCtrl(command):
	if command == 'laugh':
		showLook(LaughImage)


def showText(content, x, y):
	draw.text((x, y), content, fill=255)
	disp.image(image)
	disp.display()

'''
while 1:
	showLook(LaughImage)
'''
if __name__ == '__main__':
	while 1:
		showText('123421',0,0)
		time.sleep(1)
		disp.clear()
		disp.display()
		time.sleep(1)