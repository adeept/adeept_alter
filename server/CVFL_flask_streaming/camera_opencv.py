import os
import cv2
from base_camera import BaseCamera
import numpy as np
import time
import threading
import imutils

'''
Set the color of the line, 255 is white line, 0 is black line
'''
lineColorSet = 255
'''
Set the reference horizontal position, the larger the value, the lower, 
but it cannot be greater than the vertical resolution of the video (default 480)
'''
linePos = 380

class Camera(BaseCamera):
	video_source = 0
	def __init__(self):
		if os.environ.get('OPENCV_CAMERA_SOURCE'):
			Camera.set_video_source(int(os.environ['OPENCV_CAMERA_SOURCE']))
		super(Camera, self).__init__()

	@staticmethod
	def set_video_source(source):
		Camera.video_source = source

	@staticmethod
	def frames():
		camera = cv2.VideoCapture(Camera.video_source)
		if not camera.isOpened():
			raise RuntimeError('Could not start camera.')

		while True:
			_, img = camera.read() #Get the picture captured by the camera

			'''
			Convert the picture to black and white, and then binarize (the value of each pixel in the picture except 0 is 255)
			'''
			img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
			retval, img =  cv2.threshold(img, 0, 255, cv2.THRESH_OTSU)
			img = cv2.erode(img, None, iterations=6)	#Use corrosion to denoise
			colorPos = img[linePos]						#Get the array of pixel values of linePos
			try:
				lineColorCount_Pos = np.sum(colorPos == lineColorSet)	#Get the number of pixels of the line color (line width)
				lineIndex_Pos = np.where(colorPos == lineColorSet)		#Get the horizontal position of the end of the line in the line of linePos
				'''
				Use the endpoint position and line width to calculate the position of the center point of the line
				'''
				left_Pos = lineIndex_Pos[0][lineColorCount_Pos-1]
				right_Pos = lineIndex_Pos[0][0]
				center_Pos = int((left_Pos+right_Pos)/2)

				print('The position of the center point of the line is：%d'%center_Pos)
			except:
				'''
				If the line is not detected, the line width above is 0 as the denominator will cause an error, 
				so you know that no line has been detected
				'''
				center_Pos = 0
				print('No line detected')

			'''
			Draw horizontal reference lines
			'''
			cv2.line(img,(0,linePos),(640,linePos),(255,255,64),1)
			if center_Pos:
				'''
				If a line is detected, draw the center point of the line
				'''
				cv2.line(img,(center_Pos,linePos+300),(center_Pos,linePos-300),(255,255,64),1)

			
			# encode as a jpeg image and return it
			yield cv2.imencode('.jpg', img)[1].tobytes()