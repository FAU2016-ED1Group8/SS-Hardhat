#  !/usr/bin/env python3
#   Simple script for shutting down the raspberry Pi at the press of a button.
#   by Inderpreet Singh
#   Requires PyAudio and PySpeech.

import RPi.GPIO as GPIO
import time
import os
import speech_recognition as sr
import datetime
import serial
from pyrebase import pyrebase
from subprocess import call
import geopy                            #geopy for coordinate comparison
from geopy.distance import vincenty     #geopy function for long/lat comparison
from geopy.geocoders import Nominatim


#    Use the Board Pin numbers
#    Setup the Pin with Internal pullups enabled and PIN in reading mode.

# __ input pins__
hazLogBtn = 29
phoneBtn = 31
cameraBtn = 33
shutdown = 35
magSensor = 37
# __ output pins __
laser = 22
wLeds = 24
buzzer = 26

ser = serial.Serial("/dev/ttyS0",115200,timeout=3)  #   FONA Serial

config = {
  "apiKey": "apiKey",
  "authDomain": "smartsafetyhardhat.firebaseapp.com",
  "databaseURL": "https://smartsafetyhardhat.firebaseio.com",
  "storageBucket": "smartsafetyhardhat.appspot.com"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

#   Our function on what to do when the button is pressed
def Shutdown():
    os.system("sudo shutdown -h now")

def getGPSCoordinates():
    #  try:
        if ser.write("AT+CGNSPWR=?") == 'OK':
            gpsLocation = ser.write("AT+CGNSINF")
            gpsLatLon = gpsLocation.split(',')
            return (gpsLatLon[3],gpsLatLon[4],gpsLatLon[2])


    #  except:
        #  log error
def capturePicture():
    #  add naming code for image
    call(["fswebcam -r 640x480 --save image4.jpg"])
    print("image4 captured")


def recHazLog():

    #time variable
    now = datetime.datetime.now()
    timeStr = now.strftime('%A %B %d, %Y %I:%M:%S %p')

    #dummy message to write to database
    message = "Huckleberry"

    #retrieves number of substations from firebase
    num_of_substations = list(range(len([users.key() for users in (db.child("Substation Data").get()).each()])))

    #gets the latitude/longtitude of each substation from firebase
    station_lat = [(db.child("Substation Data").child(str(x)).child("latitude").get()).val() for x in num_of_substations ]
    station_long = [(db.child("Substation Data").child(str(x)).child("longitude").get()).val() for x in num_of_substations ]

    #variables that holds the lat/long coordinates of the subsations
    k =  list (zip(station_lat, station_long))

    #dummy long/lat coordinates for location of hazard report
    loc_of_report = (latitude, longitude)

    # Record Audio
    r = sr.Recognizer()
    with sr.Microphone() as source:

        print("Say something!")
        # -- Replace with buzzer --
        audio = r.listen(source)

    # Speech recognition using Google Speech Recognition
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        print("You said: " + r.recognize_google(audio))
        google_translate = r.recognize_google(audio)
        #data = {"name": google_translate, "date": time }
        #db.child("hazards").push(data)

        #loop that will write the report to firebase (it will write to a specific node in the database)
        for p in k:
            if vincenty(loc_of_report, p).miles <= 2:                               #does the compare and the radius of 2 miles
                    print(k.index(p))                                               #prints the index of the subsation
                    data = {"hazardreport": google_translate, "date": timeStr}         #variable that will be written to the database
                    db.child("substation"+str(k.index(p))+"hazards").push(data)     #writes to the correct node to the database
            else:
                    print("no match")                                               #have to do something else in the future. Not known yet.

    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand audio")
    except sr.RequestError as e:
        print("Could not request results from Google Speech Recognition service; {0}".format(e))


def checkMagField():
    print("magnetic field detected")


def startCall():
    #  ser = serial.Serial("/dev/ttyUSB0",115200,timeout=3) #  FONA Serial
    print("insideStartCall")

    inputnum=str('5618438458')
    ser.write("ATD"+str(inputnum)+";\r")
    ser.close()
    #
    # else:   #   answercall():
    #     print("Answering Call")
    #     ser.write("ATA\r")
    #     data=""
    #     data=ser.read(10)
    #
    #
    # while True :
    #     input_value=gpio.input(callbutton)
    #     if input_value==False:  #  bcall button is pressed
    #         print ("press")
    #         call()
    #         while innput_value==False:
    #             input_value=gpio.input(callbutton)



#  def endCall(channel):

#   Add our function to execute when the button pressed event happens / function called on button down

#   Now wait!

def callButton():
    print("Call function")
    # callState = ser.write('')
    startCall()

#    time variable
now = datetime.datetime.now()
timeStr = now.strftime('%A %B %d, %Y %I:%M:%S %p')
#  time = str(datetime.datetime.now())

GPIO.setmode(GPIO.BOARD)

GPIO.setup(hazLogBtn, GPIO.IN)  #   log hazard
GPIO.setup(phoneBtn, GPIO.IN)  #   start end call
GPIO.setup(cameraBtn, GPIO.IN)  #   camera
GPIO.setup(shutdown, GPIO.IN)  #   shutdown
GPIO.setup(magSensor, GPIO.IN)  #   mag sensor

GPIO.setup(laser, GPIO.OUT)  #   laser
GPIO.setup(wLeds, GPIO.OUT)  #   warning LEDs
GPIO.setup(buzzer, GPIO.OUT, initial=0)  #   Buzzer

GPIO.add_event_detect(hazLogBtn, GPIO.FALLING, callback = recHazLog, bouncetime = 2000)         #  board 29
GPIO.add_event_detect(phoneBtn, GPIO.FALLING, callback = callButton, bouncetime = 2000)      #  board 31
GPIO.add_event_detect(cameraBtn, GPIO.FALLING, callback = capturePicture, bouncetime = 2000)   #  board 33
GPIO.add_event_detect(shutdown, GPIO.FALLING, callback = Shutdown, bouncetime = 2000)         #  board 37
GPIO.add_event_detect(magSensor, GPIO.FALLING, callback = checkMagField, bouncetime = 2000)         #  board 21


while 1:
   try:
      time.sleep(1)
   except KeyboardInterrupt:
      raise
   except:
      print("something went wrong!")
