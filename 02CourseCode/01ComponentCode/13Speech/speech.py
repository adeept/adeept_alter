#!/usr/bin/python3
# File name   : speech.py
# Description : Speech Recognition 
# Website     : www.adeept.com
# E-mail      : support@adeept.com
# Author      : William & Authors from https://github.com/Uberi/speech_recognition#readme
# Date        : 2018/10/12
import speech_recognition as sr

r = sr.Recognizer()
v_command = ''

while True:
    with sr.Microphone(device_index =2,sample_rate=48000) as source:
        r.record(source,duration=2)
        print("What is your command?")
        audio = r.listen(source)

    try:
        v_command = r.recognize_sphinx(audio,
        keyword_entries=[('forward',1.0),('backward',1.0),
        ('left',1.0),('right',1.0),('stop',1.0)])        #You can add your own command here
        print(v_command)
    except sr.UnknownValueError:
        print("say again")
    except sr.RequestError as e:
        pass

    if 'forward' in v_command:
        print('you can put move forward function here')

    elif 'backward' in v_command:
        print('you can put move backward function here')

    elif 'left' in v_command:
        print('you can put turn left function here')

    elif "right" in v_command:
        print('you can put turn right function here')

    elif 'stop' in v_command:
        print('you can put stop function here')

    else:
        pass