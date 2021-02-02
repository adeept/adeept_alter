#Import the library for controlling the OLED screen and delay time
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306
import time

#Instantiate the object used to control the OLED
serial = i2c(port=1, address=0x3C)
device = ssd1306(serial, rotate=0)

#Write the text "ROBOT" at the position (0, 20) on the OLED screen
with canvas(device) as draw:
    draw.text((0, 20), "ROBOT", fill="white")

while True:
    time.sleep(10)