#!/usr/bin/env/python
# File name   : server.py
# Production  : RaspTankPro
# Website     : www.adeept.com
# Author      : William
# Date        : 2020/03/17

import time
import threading
import os
import info
import socket

#websocket
import asyncio
import websockets

import json
import app


curpath = os.path.realpath(__file__)
thisPath = "/" + os.path.dirname(curpath)


def ap_thread():
    os.system("sudo create_ap wlan0 eth0 Alter 12345678")


def wifi_check():
    try:
        s =socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        s.connect(("1.1.1.1",80))
        ipaddr_check=s.getsockname()[0]
        s.close()
        print(ipaddr_check)
    except:
        ap_threading=threading.Thread(target=ap_thread)   #Define a thread for data receiving
        ap_threading.setDaemon(True)                          #'True' means it is a front thread,it would close when the mainloop() closes
        ap_threading.start()                                  #Thread starts


async def check_permit(websocket):
    while True:
        recv_str = await websocket.recv()
        cred_dict = recv_str.split(":")
        if cred_dict[0] == "admin" and cred_dict[1] == "123456":
            response_str = "congratulation, you have connect with server\r\nnow, you can do something else"
            await websocket.send(response_str)
            return True
        else:
            response_str = "sorry, the username or password is wrong, please submit again"
            await websocket.send(response_str)

async def recv_msg(websocket):
    while True: 
        response = {
            'status' : 'ok',
            'title' : '',
            'data' : None
        }

        data = ''
        data = await websocket.recv()
        try:
            data = json.loads(data)
        except Exception as e:
            print('not A JSON')

        if not data:
            continue

        if isinstance(data,str):
            flask_app.commandInput(data)

            if 'get_info' == data:
                response['title'] = 'get_info'
                response['data'] = [info.get_cpu_tempfunc(), info.get_cpu_use(), info.get_ram_info()]

            if 'findColor' == data:
                flask_app.modeselect('findColor')
                print('set mode as findColor')

            elif 'motionGet' == data:
                flask_app.modeselect('watchDog')
                print('set mode as watchDog')

            elif 'stopCV' == data:
                flask_app.modeselect('none')

            #CVFL
            elif 'CVFL' == data:
                flask_app.modeselect('findlineCV')
                print('set mode as findlineCV')

            elif 'CVFLColorSet' in data:
                color = int(data.split()[1])
                flask_app.camera.colorSet(color)

            elif 'CVFLL1' in data:
                pos = int(data.split()[1])
                flask_app.camera.linePosSet_1(pos)

            elif 'CVFLL2' in data:
                pos = int(data.split()[1])
                flask_app.camera.linePosSet_2(pos)

            elif 'CVFLSP' in data:
                err = int(data.split()[1])
                flask_app.camera.errorSet(err)

            elif 'defEC' in data:#Z
                fpv.defaultExpCom()

        elif(isinstance(data,dict)):
            if data['title'] == "findColorSet":
                color = data['data']
                flask_app.colorFindSet(color[0],color[1],color[2])

        print(data)
        response = json.dumps(response)
        await websocket.send(response)

async def main_logic(websocket, path):
    await check_permit(websocket)
    await recv_msg(websocket)

if __name__ == '__main__':
    HOST = ''
    PORT = 10223                              #Define port serial 
    BUFSIZ = 1024                             #Define buffer size
    ADDR = (HOST, PORT)

    global flask_app
    flask_app = app.webapp()
    flask_app.startthread()

    # flask_app.commandInput('breathLight', [92, 128, 255])

    while  1:
        wifi_check()
        try:                  #Start server,waiting for client
            start_server = websockets.serve(main_logic, '0.0.0.0', 8888)
            asyncio.get_event_loop().run_until_complete(start_server)
            print('waiting for connection...')
            break
        except Exception as e:
            print(e)

    try:
        flask_app.commandInput('looks', 'laugh')
        flask_app.commandInput('setWS', [92, 128, 255])
        asyncio.get_event_loop().run_forever()
    except Exception as e:
        print(e)
