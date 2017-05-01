#!/home/pi/SS-Hardhat/tractus/bin/python

import RPi.GPIO as GPIO
import time
import os
import speech_recognition as sr
from datetime import datetime as dt
import serial
from pyrebase import pyrebase
from subprocess import call
import geopy                            #geopy for coordinate comparison
from geopy.distance import vincenty     #geopy function for long/lat comparison
from geopy.geocoders import Nominatim
from fuzzywuzzy import fuzz             #string compare module
from fuzzywuzzy import process

ser = serial.Serial("/dev/ttyS0",115200,timeout=3)  #   FONA Serial

def check_phone_state():
    print("Checking for dialtone")
    # if dialtone start_call
    sercom = "at+cpas\r"
    ser.write(sercom.encode())
    while True:
        try:
            state=ser.readline()
            # print(state)
            if str(state,'ascii')=='+CPAS: 0\r\n':
                print("Phone ready")
                start_call()
            elif str(state,'ascii')=='+CPAS: 4\r\n':
                sercom = "ath\r"
                ser.write(sercom.encode())
        except:
            pass


    # elif no_dialton end_call()

def start_call():
    inputnum=str('5618438458')
    print("Starting call")
    callingVar = 'ATD%s;\r\n' % inputnum
    ser.write(callingVar.encode())
    print('Calling now: $d' % inputnum)


check_phone_state()
