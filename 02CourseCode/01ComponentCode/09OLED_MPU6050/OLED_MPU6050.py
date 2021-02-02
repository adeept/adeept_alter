from mpu6050 import mpu6050
import time

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306

sensor = mpu6050(0x68)

serial = i2c(port=1, address=0x3C)
device = ssd1306(serial, rotate=0)


while 1:
	xyzGet = sensor.get_accel_data()	#Obtain XYZ reading information from the sensor

	xGet = xyzGet['x'] # Get x-axis reading
	yGet = xyzGet['y'] # Get y-axis reading
	zGet = xyzGet['z'] # Get z-axis reading

	#Display the XYZ three-axis value on the OLED
	with canvas(device) as draw:
		draw.text((0, 0), str(xGet), fill="white")
		draw.text((0, 20), str(yGet), fill="white")
		draw.text((0, 40), str(zGet), fill="white")

	time.sleep(0.1)