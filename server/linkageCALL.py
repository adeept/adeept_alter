import alterMove
import time

'''
Just call the alterMove.linkageQ(leg, x, y) function directly
Where leg can be 1, 2, 3, 4 corresponding to four legs respectively

Specifically：

1-forward-3
|		  |
|		  |
|		  |
|		  |
2—————————4

The x, y parameters are the coordinates of the location, the greater the positive value of x, the more the location is toward the forward direction
The greater the positive value of y, the more the landing point is towards the ground

When you control the location of each leg, there is no need to instantiate the Alter object
Because the main purpose of instantiating Alter objects is for multi-threaded control

You can choreograph or edit other actions for the robot by programming the location and setting the appropriate delay time

The following routines control the swing of the robot's 1, 2, 3, and 4 legs, and you can intuitively understand how to call the function
'''
while 1:
	alterMove.linkageQ(1, 15, 50)
	time.sleep(1)

	alterMove.linkageQ(2, 15, 50)
	time.sleep(1)

	alterMove.linkageQ(3, 15, 50)
	time.sleep(1)

	alterMove.linkageQ(4, 15, 50)
	time.sleep(1)

	alterMove.linkageQ(1, -15, 50)
	time.sleep(1)

	alterMove.linkageQ(2, -15, 50)
	time.sleep(1)

	alterMove.linkageQ(3, -15, 50)
	time.sleep(1)

	alterMove.linkageQ(4, -15, 50)
	time.sleep(1)