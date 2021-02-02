import os
from PIL import Image
import time

jpgPath = 'jpg/' # Import the location of the jpg image
ppmPath = 'ppm/' # Where to export the ppm image

jpgNames = os.listdir(jpgPath) # Get the file names of all jpe images in the jpg folder


for frameName in jpgNames: # Convert one by one
	image = Image.open(jpgPath+frameName) # Open a jpg graphic
	newName = frameName[:-4]+'.ppm'		# For the new name, delete the .jpg from the original name and add .ppm
	image.save((ppmPath+newName), 'ppm') # Save as a file in ppm format, saved in the ppm folder