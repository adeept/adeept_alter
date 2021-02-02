import os
import cv2
from base_camera import BaseCamera
import numpy as np

'''
Set the target color, HSV color space
'''
colorUpper = np.array([44, 255, 255])
colorLower = np.array([24, 100, 100])

font = cv2.FONT_HERSHEY_SIMPLEX

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
			# read current frame
			_, img = camera.read() #Get the picture captured by the camera

			hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)	#Convert the captured image to HSV color space
			mask = cv2.inRange(hsv, colorLower, colorUpper)	#Traverse the colors in the target color range in the HSV color space screen, and turn these color blocks into masks
			mask = cv2.erode(mask, None, iterations=2)	#Corrosion of small blocks of mask (noise) in the picture (small blocks of color or noise disappear)
			mask = cv2.dilate(mask, None, iterations=2)	#Expansion, the large mask that was reduced in the previous step is restored to its original size
			cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
				cv2.CHAIN_APPROX_SIMPLE)[-2]			#Find a few masks in the screen
			center = None  		
			if len(cnts) > 0:	#If the number of entire masks in the screen is greater than one
				'''
				Find the center point coordinates of the object of the target color and the size of the object in the screen
				'''
				c = max(cnts, key=cv2.contourArea)
				((box_x, box_y), radius) = cv2.minEnclosingCircle(c)
				M = cv2.moments(c)
				center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
				X = int(box_x)
				Y = int(box_y)
				'''
				Get the center point coordinates of the target color object and output
				'''
				print('Target color object detected')
				print('X:%d'%X)
				print('Y:%d'%Y)
				print('-------')

				'''
				Write text on the screen: Target Detected
				'''
				cv2.putText(img,'Target Detected',(40,60), font, 0.5,(255,255,255),1,cv2.LINE_AA)
				'''
				Draw a frame around the target color object
				'''
				cv2.rectangle(img,(int(box_x-radius),int(box_y+radius)),(int(box_x+radius),int(box_y-radius)),(255,255,255),1)
			else:
				cv2.putText(img,'Target Detecting',(40,60), font, 0.5,(255,255,255),1,cv2.LINE_AA)
				print('The target color object is not detected')
			
			# encode as a jpeg image and return it
			yield cv2.imencode('.jpg', img)[1].tobytes()