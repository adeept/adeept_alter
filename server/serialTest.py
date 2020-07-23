#!/usr/bin/python3

import serial
import time
import threading

ser = serial.Serial("/dev/ttyAMA0", 9600)

def rcv_data():
	while True:
		print('1')
		rcv=ser.readline()
		rcv=rcv.decode() 
		print(rcv)

def main():
	# sendNum = ser.write('ec01500300888f'.encode())
	# sendNum = ser.write('0103000000255f'.encode())
	# sendNum = ser.write('ec010000000000'.encode())
	# print('sendNum:',sendNum)
	# time.sleep(0.5)

	th=threading.Thread(target=rcv_data)
	th.setDaemon(True)
	th.start()

	while True:
		'''
		count = ser.inWaiting()
		if count != 0:
			# 读取内容并回显
			recv = ser.read(count)
			ser.write(recv)
		# 清空接收缓冲区
		ser.flushInput()
		# 必要的软件延时
		'''

		'''
		sendNum = ser.write('0103000000255f'.encode())
		time.sleep(2)
		print('sendNum:',sendNum)
		'''
		# sendNum = ser.write('ec015003**888f'.encode())
		sendNum = ser.write('0103000000255f'.encode())
		ser.flushInput()
		print('sendNum:',sendNum)
		time.sleep(1)


	
if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		if ser != None:
			ser.close()