#!/usr/bin/env/python
# File name   : server.py
# Production  : Gtank
# Website     : www.gewbot.com
# E-mail      : gewubot@163.com
# Author      : William
# Date        : 2019/10/28

import socket
import alterMove

alter = alterMove.Alter()
alter.start()

screen = alterMove.OLED()
screen.start()

directionCommand = 'no'
turningCommand   = 'no'
speedMove = 100

posUD = 0


def app_ctrl():
    app_HOST = ''
    app_PORT = 10123
    app_BUFSIZ = 1024
    app_ADDR = (app_HOST, app_PORT)

    def  ap_thread():
        os.system("sudo create_ap wlan0 eth0 Car 12345678")

    def appCommand(data_input):
        global directionCommand, turningCommand, speedMove, posUD
        if data_input == 'forwardStart\n':
            directionCommand = 'forward'
            alter.moveAlter(speedMove, directionCommand, turningCommand, 0)

        elif data_input == 'backwardStart\n':
            directionCommand = 'backward'
            alter.moveAlter(speedMove, directionCommand, turningCommand, 0)

        elif data_input == 'leftStart\n':
            turningCommand = 'left'
            alter.moveAlter(speedMove, directionCommand, turningCommand, 0)

        elif data_input == 'rightStart\n':
            turningCommand = 'right'
            alter.moveAlter(speedMove, directionCommand, turningCommand, 0)

        elif 'forwardStop' in data_input:
            directionCommand = 'no'
            alter.moveAlter(speedMove, directionCommand, turningCommand, 0)

        elif 'backwardStop' in data_input:
            directionCommand = 'no'
            alter.moveAlter(speedMove, directionCommand, turningCommand, 0)

        elif 'leftStop' in data_input:
            turningCommand = 'no'
            alter.moveAlter(speedMove, directionCommand, turningCommand, 0)

        elif 'rightStop' in data_input:
            turningCommand = 'no'
            alter.moveAlter(speedMove, directionCommand, turningCommand, 0)


        if data_input == 'lookLeftStart\n':
            alterMove.pitchRoll(0, 15)

        elif data_input == 'lookRightStart\n': 
            alterMove.pitchRoll(0, -15)

        elif data_input == 'downStart\n':
            posUpDown('down',5)

        elif data_input == 'upStart\n':
            posUpDown('up',5)

        elif 'lookLeftStop' in data_input:
            alterMove.pitchRoll(0, 0)
        elif 'lookRightStop' in data_input:
            alterMove.pitchRoll(0, 0)
        elif 'downStop' in data_input:
            alterMove.pitchRoll(0, 0)
        elif 'upStop' in data_input:
            alterMove.pitchRoll(0, 0)

        if data_input == 'aStart\n':
            alterMove.frontLightCtrl('on')

        elif data_input == 'bStart\n':
            screen.showLooks('laugh')

        elif data_input == 'cStart\n':
            alter.functionSelect('findline')

        elif data_input == 'dStart\n':
            alter.functionSelect('steady')

        elif 'aStop' in data_input:
            alterMove.frontLightCtrl('off')
        elif 'bStop' in data_input:
            pass
        elif 'cStop' in data_input:
            alter.functionSelect('no')
            alter.moveStop()
        elif 'dStop' in data_input:
            alter.functionSelect('no')
            alter.moveStop()

        print(data_input)

    def appconnect():
        global AppCliSock, AppAddr
        try:
            s =socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
            s.connect(("1.1.1.1",80))
            ipaddr_check=s.getsockname()[0]
            s.close()
            print(ipaddr_check)

            AppSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            AppSerSock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            AppSerSock.bind(app_ADDR)
            AppSerSock.listen(5)
            print('waiting for App connection...')
            AppCliSock, AppAddr = AppSerSock.accept()
            print('...App connected from :', AppAddr)
        except:
            ap_threading=threading.Thread(target=ap_thread)   #Define a thread for data receiving
            ap_threading.setDaemon(True)                          #'True' means it is a front thread,it would close when the mainloop() closes
            ap_threading.start()                                  #Thread starts

            AppSerSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            AppSerSock.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
            AppSerSock.bind(app_ADDR)
            AppSerSock.listen(5)
            print('waiting for App connection...')
            AppCliSock, AppAddr = AppSerSock.accept()
            print('...App connected from :', AppAddr)


    appconnect()

    app_threading=threading.Thread(target=appconnect)         #Define a thread for FPV and OpenCV
    app_threading.setDaemon(True)                             #'True' means it is a front thread,it would close when the mainloop() closes
    app_threading.start()                                     #Thread starts

    while 1:
        data = ''
        data = str(AppCliSock.recv(app_BUFSIZ).decode())
        if not data:
            continue
        appCommand(data)
        pass

AppConntect_threading=threading.Thread(target=app_ctrl)         #Define a thread for FPV and OpenCV
AppConntect_threading.setDaemon(True)                             #'True' means it is a front thread,it would close when the mainloop() closes
AppConntect_threading.start()                                     #Thread starts


if __name__ == '__main__':
    i = 1
    try:
        while 1:
            i += 1
            print(i)
            time.sleep(30)
            pass
    except:
        pass