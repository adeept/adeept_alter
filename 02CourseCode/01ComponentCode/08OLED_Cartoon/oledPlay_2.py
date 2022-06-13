
'''
When the oledPlay.py file runs and reports an error, please run the file.
Reference: https://github.com/adafruit/Adafruit_CircuitPython_SSD1306/blob/main/examples/ssd1306_pillow_image_display.py
'''
#!/usr/bin/python3
import time
import os
os.system("sudo pip3 install adafruit-circuitpython-ssd1306")
#Import OLED screen related libraries
import Adafruit_GPIO.SPI as SPI
import adafruit_ssd1306
import board

#Import libraries for image processing
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

#Obtain the absolute path of this file
curpath = os.path.realpath(__file__)
thisPath = "/" + os.path.dirname(curpath) + "/"

#OLED screen initialization
RST = 24
i2c = board.I2C()
#oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C, reset=RST)
oled = adafruit_ssd1306.SSD1306_I2C(128, 64, i2c, addr=0x3C)


#Set playback frame rate
FPS = 30

#Calculate the delay time per frame according to the playback frame rate
timeDelay = 1/FPS

#Clear the screen
oled.fill(0)
oled.show()

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
	image = (
    Image.open(thisPath+ppmPath+frameName)
    .resize((oled.width, oled.height), Image.BICUBIC)
    .convert('1'))
	#Store the converted image into LaughImage
	LaughImage.append(image)


#Displaying frame by frame is equivalent to playing a cartoon
for i in range(0, len(LaughImage)):
	oled.image(LaughImage[i])
	oled.show()
	time.sleep(timeDelay)