from mpu6050 import mpu6050
import time

sensor = mpu6050(0x68)


while 1:
	xyzGet = sensor.get_accel_data()	#Obtain XYZ reading information from the sensor

	xGet = xyzGet['x'] # Get x-axis reading
	yGet = xyzGet['y'] # Get y-axis reading
	zGet = xyzGet['z'] # Get z-axis reading

	print(xGet, yGet, zGet)
	time.sleep(0.5)