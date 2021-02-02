#!/usr/bin/env/python3
# File name   : server.py
# Description : for OLED functions
# Website	 : www.gewbot.com
# Author	  : William(Based on Adrian Rosebrock's OpenCV code on pyimagesearch.com)
# Date		: 2019/08/28

from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import ssd1306, ssd1325, ssd1331, sh1106
import time
import threading

try:
	serial = i2c(port=1, address=0x3C)
	device = ssd1306(serial, rotate=0)
except:
	print('OLED disconnected\n')


'''
Set the initial content of each line
'''
text_1 = 'HELLO WORLD'
text_2 = 'IP:CONNECTING'
text_3 = '<ARM> OR <PT> MODE'
text_4 = 'MPU6050 DETECTING'
text_5 = 'FUNCTION OFF'
text_6 = 'Message:None'

class OLED_ctrl(threading.Thread):
	def __init__(self, *args, **kwargs):
		super(OLED_ctrl, self).__init__(*args, **kwargs)
		self.__flag = threading.Event()	 # ID used to pause the thread
		self.__flag.set()	   # Set to True
		self.__running = threading.Event()	  # ID used to stop the thread
		self.__running.set()	  # Set running to True

	def run(self):
		while self.__running.isSet():
			self.__flag.wait()	  # Return immediately when it is True, and block until the internal identification bit is True when it is False.
			try:
				with canvas(device) as draw:
					draw.text((0, 0), text_1, fill="white")
					draw.text((0, 10), text_2, fill="white")
					draw.text((0, 20), text_3, fill="white")
					draw.text((0, 30), text_4, fill="white")
					draw.text((0, 40), text_5, fill="white")
					draw.text((0, 50), text_6, fill="white")
			except:
				pass
			print('loop')
			self.pause()

	def pause(self):
		self.__flag.clear()	 # Set to False to block the thread

	def resume(self):
		self.__flag.set()	# Set to True, let the thread stop blocking

	def stop(self):
		self.__flag.set()	   # Resume the thread from the suspended state, if it has been suspended
		self.__running.clear()		#Set to False

	def screen_show(self, position, text):
		'''
		Call this function to control the OLED screen, where position is the line number where you want to change the content, which can be 1-6, and text is the content
		'''
		global text_1, text_2, text_3, text_4, text_5, text_6
		if position == 1:
			text_1 = text
		elif position == 2:
			text_2 = text
		elif position == 3:
			text_3 = text
		elif position == 4:
			text_4 = text
		elif position == 5:
			text_5 = text
		elif position == 6:
			text_6 = text
		self.resume()

if __name__ == '__main__':
	'''
	Instantiate the OLED screen object
	'''
	screen = OLED_ctrl()

	'''
	Start this thread
	'''
	screen.start()

	'''
	Set the content of the first line to 12345678
	'''
	screen.screen_show(1, '123345678')

	'''
	Since the above operation will not block the thread, we need to loop here to avoid the program exit after the execution is complete
	'''
	while 1:
		time.sleep(10)
		pass