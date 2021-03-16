import os
import cv2
from base_camera import BaseCamera
import ultra
import numpy as np
import alterMove
import datetime
import Kalman_filter
import PID
import time
import threading
import imutils

alter = alterMove.Alter()
alter.start()

screen = alterMove.OLED()
screen.start()

alterMove.frontLightCtrl('on')

pid = PID.PID()
pid.SetKp(0.5)
pid.SetKd(0)
pid.SetKi(0)

CVRun = 1
linePos_1 = 440
linePos_2 = 380
lineColorSet = 255
frameRender = 1
findLineError = 20

colorUpper = np.array([44, 255, 255])
colorLower = np.array([24, 100, 100])

directionCommand = 'no'
turningCommand   = 'no'
speedMove = 100

posUD = 0

distanceCheak = 0.6

def posUpDown(command, spd):
    global posUD
    if command == 'up':
        if posUD < 15:
            posUD += spd
        else:
            posUD = 15
    elif command == 'down':
        if posUD > -15:
            posUD -= spd
        else:
            posUD = -15
    alterMove.pitchRoll(posUD, 0)



class CVThread(threading.Thread):
    font = cv2.FONT_HERSHEY_SIMPLEX

    # kalman_filter_X =  Kalman_filter.Kalman_filter(0.01,0.1)
    # kalman_filter_Y =  Kalman_filter.Kalman_filter(0.01,0.1)
    P_direction = 1
    T_direction = 1
    P_servo = 0
    T_servo = 4
    P_anglePos = 0
    T_anglePos = 0
    cameraDiagonalW = 64
    cameraDiagonalH = 48
    videoW = 640
    videoH = 480
    Y_lock = 0
    X_lock = 0
    tor = 17

    aspd = 0.01

    # scGear = RPIservo.ServoCtrl()
    # scGear.moveInit()
    # switch.switchSetup()

    def __init__(self, *args, **kwargs):
        self.CVThreading = 0
        self.CVMode = 'none'
        self.imgCV = None

        self.mov_x = None
        self.mov_y = None
        self.mov_w = None
        self.mov_h = None

        self.radius = 0
        self.box_x = None
        self.box_y = None
        self.drawing = 0

        self.findColorDetection = 0

        self.left_Pos1 = None
        self.right_Pos1 = None
        self.center_Pos1 = None

        self.left_Pos2 = None
        self.right_Pos2 = None
        self.center_Pos2 = None

        self.center = None

        super(CVThread, self).__init__(*args, **kwargs)
        self.__flag = threading.Event()
        self.__flag.clear()

        self.avg = None
        self.motionCounter = 0
        self.lastMovtionCaptured = datetime.datetime.now()
        self.frameDelta = None
        self.thresh = None
        self.cnts = None

    def mode(self, invar, imgInput):
        self.CVMode = invar
        self.imgCV = imgInput
        self.resume()

    def elementDraw(self,imgInput):
        if self.CVMode == 'none':
            pass

        elif self.CVMode == 'findColor':
            if self.findColorDetection:
                cv2.putText(imgInput,'Target Detected',(40,60), CVThread.font, 0.5,(255,255,255),1,cv2.LINE_AA)
                self.drawing = 1
            else:
                cv2.putText(imgInput,'Target Detecting',(40,60), CVThread.font, 0.5,(255,255,255),1,cv2.LINE_AA)
                self.drawing = 0

            if self.radius > 10 and self.drawing:
                cv2.rectangle(imgInput,(int(self.box_x-self.radius),int(self.box_y+self.radius)),(int(self.box_x+self.radius),int(self.box_y-self.radius)),(255,255,255),1)

        elif self.CVMode == 'findlineCV':
            if frameRender:
                imgInput = cv2.cvtColor(imgInput, cv2.COLOR_BGR2GRAY)
                retval_bw, imgInput =  cv2.threshold(imgInput, 0, 255, cv2.THRESH_OTSU)
                imgInput = cv2.erode(imgInput, None, iterations=6)
            try:
                if lineColorSet == 255:
                    cv2.putText(imgInput,('Following White Line'),(30,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(128,255,128),1,cv2.LINE_AA)
                else:
                    cv2.putText(imgInput,('Following Black Line'),(30,50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,(128,255,128),1,cv2.LINE_AA)

                cv2.line(imgInput,(self.left_Pos1,(linePos_1+30)),(self.left_Pos1,(linePos_1-30)),(255,128,64),1)
                cv2.line(imgInput,(self.right_Pos1,(linePos_1+30)),(self.right_Pos1,(linePos_1-30)),(64,128,255),)
                cv2.line(imgInput,(0,linePos_1),(640,linePos_1),(255,255,64),1)

                cv2.line(imgInput,(self.left_Pos2,(linePos_2+30)),(self.left_Pos2,(linePos_2-30)),(255,128,64),1)
                cv2.line(imgInput,(self.right_Pos2,(linePos_2+30)),(self.right_Pos2,(linePos_2-30)),(64,128,255),1)
                cv2.line(imgInput,(0,linePos_2),(640,linePos_2),(255,255,64),1)

                cv2.line(imgInput,((self.center-20),int((linePos_1+linePos_2)/2)),((self.center+20),int((linePos_1+linePos_2)/2)),(0,0,0),1)
                cv2.line(imgInput,((self.center),int((linePos_1+linePos_2)/2+20)),((self.center),int((linePos_1+linePos_2)/2-20)),(0,0,0),1)
            except:
                pass

        elif self.CVMode == 'watchDog':
            if self.drawing:
                cv2.rectangle(imgInput, (self.mov_x, self.mov_y), (self.mov_x + self.mov_w, self.mov_y + self.mov_h), (128, 255, 0), 1)

        return imgInput


    def watchDog(self, imgInput):
        timestamp = datetime.datetime.now()
        gray = cv2.cvtColor(imgInput, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        if self.avg is None:
            print("[INFO] starting background model...")
            self.avg = gray.copy().astype("float")
            return 'background model'

        cv2.accumulateWeighted(gray, self.avg, 0.5)
        self.frameDelta = cv2.absdiff(gray, cv2.convertScaleAbs(self.avg))

        # threshold the delta image, dilate the thresholded image to fill
        # in holes, then find contours on thresholded image
        self.thresh = cv2.threshold(self.frameDelta, 5, 255,
            cv2.THRESH_BINARY)[1]
        self.thresh = cv2.dilate(self.thresh, None, iterations=2)
        self.cnts = cv2.findContours(self.thresh.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)
        self.cnts = imutils.grab_contours(self.cnts)
        # print('x')
        # loop over the contours
        for c in self.cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < 5000:
                continue
     
            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
            (self.mov_x, self.mov_y, self.mov_w, self.mov_h) = cv2.boundingRect(c)
            self.drawing = 1
            
            self.motionCounter += 1

            self.lastMovtionCaptured = timestamp
            screen.showLooks('laugh')
            alterMove.frontLightCtrl('on')

        if (timestamp - self.lastMovtionCaptured).seconds >= 0.5:
            self.drawing = 0
            alterMove.frontLightCtrl('off')
        self.pause()


    def findLineCtrl(self, posInput, setCenter):#2
        if not posInput:
            return

        if posInput > (setCenter + findLineError):
            #turnRight
            if CVRun:
                alter.moveAlter(speedMove, 'no', 'right', 0)
            else:
                alter.moveAlter(speedMove, 'no', 'no', 0)
                alter.moveStop()
            pass
        elif posInput < (setCenter - findLineError):
            #turnLeft
            if CVRun:
                alter.moveAlter(speedMove, 'no', 'left', 0)
            else:
                alter.moveAlter(speedMove, 'no', 'no', 0)
                alter.moveStop()
            pass
        else:
            #forward
            if CVRun:
                alter.moveAlter(speedMove, 'forward', 'no', 0)
            else:
                alter.move(80, 'no', 'no', 0.5)


    def findlineCV(self, frame_image):
        frame_findline = cv2.cvtColor(frame_image, cv2.COLOR_BGR2GRAY)
        retval, frame_findline =  cv2.threshold(frame_findline, 0, 255, cv2.THRESH_OTSU)
        frame_findline = cv2.erode(frame_findline, None, iterations=6)
        colorPos_1 = frame_findline[linePos_1]
        colorPos_2 = frame_findline[linePos_2]
        try:
            lineColorCount_Pos1 = np.sum(colorPos_1 == lineColorSet)
            lineColorCount_Pos2 = np.sum(colorPos_2 == lineColorSet)

            lineIndex_Pos1 = np.where(colorPos_1 == lineColorSet)
            lineIndex_Pos2 = np.where(colorPos_2 == lineColorSet)

            if lineColorCount_Pos1 == 0:
                lineColorCount_Pos1 = 1
            if lineColorCount_Pos2 == 0:
                lineColorCount_Pos2 = 1

            self.left_Pos1 = lineIndex_Pos1[0][lineColorCount_Pos1-1]
            self.right_Pos1 = lineIndex_Pos1[0][0]
            self.center_Pos1 = int((self.left_Pos1+self.right_Pos1)/2)

            self.left_Pos2 = lineIndex_Pos2[0][lineColorCount_Pos2-1]
            self.right_Pos2 = lineIndex_Pos2[0][0]
            self.center_Pos2 = int((self.left_Pos2+self.right_Pos2)/2)

            self.center = int((self.center_Pos1+self.center_Pos2)/2)
        except:
            center = None
            pass

        self.findLineCtrl(self.center, 320)
        self.pause()


    def findColor(self, frame_image):
        hsv = cv2.cvtColor(frame_image, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, colorLower, colorUpper)#1
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE)[-2]
        center = None
        if len(cnts) > 0:
            self.findColorDetection = 1
            c = max(cnts, key=cv2.contourArea)
            ((self.box_x, self.box_y), self.radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            X = int(self.box_x)
            Y = int(self.box_y)
            error_Y = abs(240 - Y)

            if Y < 240 - CVThread.tor:
                posUpDown('up', error_Y*CVThread.aspd)
            elif Y > 240 + CVThread.tor:
                posUpDown('down', error_Y*CVThread.aspd)
            else:
                screen.showLooks('laugh')
                alterMove.frontLightCtrl('on')

        else:
            self.findColorDetection = 0
            alterMove.frontLightCtrl('off')
            # alter.moveStop()
        self.pause()


    def pause(self):
        self.__flag.clear()

    def resume(self):
        self.__flag.set()

    def run(self):
        while 1:
            self.__flag.wait()
            if self.CVMode == 'none':
                alter.moveStop()
                self.pause()
                continue
            elif self.CVMode == 'findColor':

                self.CVThreading = 1
                self.findColor(self.imgCV)
                self.CVThreading = 0
            elif self.CVMode == 'findlineCV':

                self.CVThreading = 1
                self.findlineCV(self.imgCV)
                self.CVThreading = 0
            elif self.CVMode == 'watchDog':

                self.CVThreading = 1
                self.watchDog(self.imgCV)
                self.CVThreading = 0
            pass


class Camera(BaseCamera):
    video_source = 0
    modeSelect = 'none'
    # modeSelect = 'findlineCV'
    # modeSelect = 'findColor'
    # modeSelect = 'watchDog'


    def __init__(self):
        if os.environ.get('OPENCV_CAMERA_SOURCE'):
            Camera.set_video_source(int(os.environ['OPENCV_CAMERA_SOURCE']))
        super(Camera, self).__init__()

    def alterStop(self):
        alter.moveStop()
        time.sleep(0.1)
        alter.moveStop()

    def colorFindSet(self, invarH, invarS, invarV):
        global colorUpper, colorLower
        HUE_1 = invarH+15
        HUE_2 = invarH-15
        if HUE_1>180:HUE_1=180
        if HUE_2<0:HUE_2=0

        SAT_1 = invarS+150
        SAT_2 = invarS-150
        if SAT_1>255:SAT_1=255
        if SAT_2<0:SAT_2=0

        VAL_1 = invarV+150
        VAL_2 = invarV-150
        if VAL_1>255:VAL_1=255
        if VAL_2<0:VAL_2=0

        colorUpper = np.array([HUE_1, SAT_1, VAL_1])
        colorLower = np.array([HUE_2, SAT_2, VAL_2])
        print('HSV_1:%d %d %d'%(HUE_1, SAT_1, VAL_1))
        print('HSV_2:%d %d %d'%(HUE_2, SAT_2, VAL_2))
        print(colorUpper)
        print(colorLower)

    def modeSet(self, invar):
        Camera.modeSelect = invar

    def CVRunSet(self, invar):
        global CVRun
        CVRun = invar

    def linePosSet_1(self, invar):
        global linePos_1
        linePos_1 = invar

    def linePosSet_2(self, invar):
        global linePos_2
        linePos_2 = invar

    def colorSet(self, invar):
        global lineColorSet
        lineColorSet = invar

    def randerSet(self, invar):
        global frameRender
        frameRender = invar

    def errorSet(self, invar):
        global findLineError
        findLineError = invar

    @staticmethod
    def set_video_source(source):
        Camera.video_source = source

    @staticmethod
    def frames():
        camera = cv2.VideoCapture(Camera.video_source)
        if not camera.isOpened():
            raise RuntimeError('Could not start camera.')

        cvt = CVThread()
        cvt.start()

        while True:
            # read current frame
            _, img = camera.read()

            if Camera.modeSelect == 'none':
                cvt.pause()
            else:
                if cvt.CVThreading:
                    pass
                else:
                    cvt.mode(Camera.modeSelect, img)
                    cvt.resume()
                try:
                    img = cvt.elementDraw(img)
                except:
                    pass

            # encode as a jpeg image and return it
            yield cv2.imencode('.jpg', img)[1].tobytes()


class Functions(threading.Thread):

    def __init__(self, *args, **kwargs):
        super(Functions, self).__init__(*args, **kwargs)
        self.__flag = threading.Event()
        self.__flag.clear()
        self.funcMode = 'no'

    def pause(self):
        self.__flag.clear()

    def resume(self):
        self.__flag.set()

    def keepDProcessing(self):
        dist = ultra.checkdist()

        if dist < distanceCheak - 0.1:
            alter.moveAlter(100, 'backward', 'no', 1)
        elif dist > distanceCheak + 0.1:
            alter.moveAlter(100, 'forward', 'no', 1)
        else:
            alter.moveStop()

        time.sleep(0.1)


    def automaticProcessing(self):
        dist = ultra.checkdist()

        if dist < distanceCheak/2:
            alter.moveAlter(100, 'no', 'left', 1)
        else:
            alter.moveAlter(100, 'forward', 'no', 1)

        time.sleep(0.1)

    def funcProcessing(self):
        if self.funcMode == 'keepDistance':
            self.keepDProcessing()
        elif self.funcMode == 'automatic':
            self.automaticProcessing()

    def functionSelect(self, funcName):
        self.funcMode = funcName
        if self.funcMode == 'no':
            alter.moveStop()
            self.pause()
            alter.moveStop()
        else:
            self.resume()

    def run(self):
        while 1:
            self.__flag.wait()
            if self.funcMode == 'no':
                alter.moveStop()
                self.pause()
                alter.moveStop()
            else:
                self.funcProcessing()
                if self.funcMode == 'no':
                    alter.moveStop()
                    self.pause()
                    alter.moveStop()


func = Functions()
func.start()


def commandAct(act, inputA):
    global directionCommand, turningCommand, speedMove, posUD
    alterMove.configPWM(act)
    if act == 'forward':
        directionCommand = 'forward'
        alter.moveAlter(speedMove, directionCommand, turningCommand, 0)
    elif act == 'backward':
        directionCommand = 'backward'
        alter.moveAlter(speedMove, directionCommand, turningCommand, 0)
    elif act == 'left':
        turningCommand = 'left'
        alter.moveAlter(speedMove, directionCommand, turningCommand, 0)
    elif act == 'right':
        turningCommand = 'right'
        alter.moveAlter(speedMove, directionCommand, turningCommand, 0)
    elif act == 'DS':
        directionCommand = 'no'
        alter.moveAlter(speedMove, directionCommand, turningCommand, 0)
    elif act == 'TS':
        turningCommand = 'no'
        alter.moveAlter(speedMove, directionCommand, turningCommand, 0)

    elif 'wsB' in act:
        speedMove = int(act.split()[1])


    elif 'grab' == act:
        # standUp
        alterMove.stay(alterMove.maxHeight)
        pass

    elif 'loose' == act:
        # stayLow
        alterMove.stay(alterMove.minHeight)
        pass

    elif 'up' == act:
        # look up
        posUpDown('up',5)
        time.sleep(0.2)
        pass

    elif 'down' == act:
        # look down
        posUpDown('down',5)
        time.sleep(0.2)
        pass

    elif 'UDstop' == act:
        # up and down stop
        pass

    elif 'lookleft' == act:
        alterMove.pitchRoll(0, 15)

    elif 'lookright' == act:
        alterMove.pitchRoll(0, -15)



    elif 'speech' == act:
        alterMove.frontLightCtrl('on')
        screen.showLooks('laugh')
        time.sleep(0.1)
        alterMove.frontLightCtrl('off')
        time.sleep(0.1)
        alterMove.frontLightCtrl('on')
        time.sleep(0.1)
        alterMove.frontLightCtrl('off')
        time.sleep(0.1)
        alterMove.frontLightCtrl('on')
        time.sleep(0.1)
        alterMove.frontLightCtrl('off')

    elif 'speechOff' == act:
        alterMove.frontLightCtrl('on')
        screen.showLooks('laugh')
        time.sleep(0.1)
        alterMove.frontLightCtrl('off')
        time.sleep(0.1)
        alterMove.frontLightCtrl('on')
        time.sleep(0.1)
        alterMove.frontLightCtrl('off')
        time.sleep(0.1)
        alterMove.frontLightCtrl('on')
        time.sleep(0.1)
        alterMove.frontLightCtrl('off')

    elif 'trackLine' == act:
        func.functionSelect('no')
        alter.functionSelect('findline')

    elif 'trackLineOff' == act:
        alter.functionSelect('no')

    elif 'KD' == act:
        func.functionSelect('keepDistance')

    elif 'automatic' == act:
        func.functionSelect('automatic')

    elif 'automaticOff' == act:
        alter.functionSelect('no')
        func.functionSelect('no')

    elif 'steadyCamera' == act:
        alter.functionSelect('steady')
        func.functionSelect('no')

    elif 'steadyCameraOff' == act:
        alter.functionSelect('no')
        func.functionSelect('no')

    elif 'police' == act:
        alterMove.startPoliceLight()

    elif 'policeOff' == act:
        alterMove.lightStop()


    elif 'Switch_1_on' == act:
        alterMove.switchCtrl(1, 1)

    elif 'Switch_2_on' == act:
        alterMove.switchCtrl(2, 1)

    elif 'Switch_3_on' == act:
        alterMove.switchCtrl(3, 1)

    elif 'Switch_1_off' == act:
        alterMove.switchCtrl(1, 0)

    elif 'Switch_2_off' == act:
        alterMove.switchCtrl(2, 0)

    elif 'Switch_3_off' == act:
        alterMove.switchCtrl(3, 0)


    elif act == 'breathLight':
        alterMove.startBreathLight(inputA[0], inputA[1], inputA[2])
    elif act == 'setWS':
        alterMove.lightStop()
        alterMove.set2812(inputA[0], inputA[1], inputA[2])

    elif act == 'looks':
        if inputA == 'laugh':
            screen.showLooks('laugh')

        else:
            screen.oledShowText(inputA, 0, 0)