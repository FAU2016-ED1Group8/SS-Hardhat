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
hazLogBtn = int(29)
phoneBtn = int(31)
cameraBtn = int(33)
shutdown = int(35)
magSensor = int(37)
# __ output pins __
laser = int(22)
wLeds = int(24)
buzzer = int(26)

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
def shutdown():
    os.system("sudo shutdown -h 'now'")

def getGPSCoordinates():
    #  try:
        if ser.write("AT+CGNSPWR=?") == 'OK':
            gpsLocation = ser.write("AT+CGNSINF")
            gpsLatLon = gpsLocation.split(',')
            return (gpsLatLon[3],gpsLatLon[4],gpsLatLon[2])


    #  except:
        #  log error
def capturePicture():
    firebase = pyrebase.initialize_app(config)

    now = dt.today().strftime("%Y%m%d%H%M%S")
    file_name = now + '.jpg'
    file_w_path = 'fswebcam -r 640x480 -S 3 --jpeg 50 --save /home/pi/SS-Hardhat/application_code/images/'+file_name
    os.system('fswebcam -r 640x480 -S 3 --jpeg 50 --save /home/pi/SS-Hardhat/application_code/images/'+file_name)
    print(file_w_path)

    #####################################################################
    #####################Write to Storage################################
    #####################################################################

    print(file_name)
    storage = firebase.storage()
    #storage.child("Camera/"+"forest").put("/home/pi/Desktop/images/forest.jpg")
    storage.child("Camera/"+file_name).put("/home/pi/SS-Hardhat/application_code/images/"+file_name)

    #####################################################################
    ####################Write to Database################################
    #####################################################################
    db = firebase.database()

    #time variable
    now = datetime.datetime.now()
    time = now.strftime('%A %B %d, %Y %I:%M:%S %p')
    token = None

    imageUrl = storage.child("Camera/"+file_name).get_url(token)

    #variable that will be written to the database
    data = {"ImageName":imageUrl, "date": time}
    db.child("Camera Data").push(data)


    print("success!")


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
    # set warning lebPin t
    print("magnetic field detected")
    for c in range(1,15):
        GPIO.output(wLeds,GPIO.HIGH)
        time.sleep(1)
        GPIO.output(wLeds,GPIO.LOW)
        time.sleep(.5)

def startCall():
    #print("insideStartCall")
    numberToDial = '5618438458' # getNumber()
    inputnum=str(numberToDial)
    ser.write("ATD"+str(inputnum)+";\r\n".encode())
    response = ser.readline()
    time.sleep(10)
    if response == "OK" :
        ser.close()
    else:
        print("Something went wrong")


def endCall(channel):

#   Add our function to execute when the button pressed event happens / function called on button down
    ser.write("ATH".encode())
    time.sleep(5)
    if response == "OK" :
        ser.close()
    else:
        print("Something went wrong")
#   Now wait!

def callButton():
    print("Call function")
    ser.write("AT+CPAS".encode())
    time.sleep(.5)
    while True:
        line = ser.readline()
        if not line.strip():  # evaluates to true when an "empty" line is received
            pass
        elif line == "OK" or line == "ERROR":
            break
        else:
            if line[-1:] == "0":
                startCall()
            elif line[-1:] == "4":
                endCall()
            else:
                time.sleep(1)
                pass



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

GPIO.add_event_detect(hazLogBtn, GPIO.FALLING, callback = recHazLog(), bouncetime = 2000)         #  board 29
GPIO.add_event_detect(phoneBtn, GPIO.FALLING, callback = callButton(), bouncetime = 2000)      #  board 31
GPIO.add_event_detect(cameraBtn, GPIO.FALLING, callback = capturePicture(), bouncetime = 2000)   #  board 33
GPIO.add_event_detect(35, GPIO.FALLING, callback = shutdown(), bouncetime = 2000)         #  board 35
GPIO.add_event_detect(magSensor, GPIO.FALLING, callback = checkMagField(), bouncetime = 2000)         #  board 37


while True:
    try:
        time.sleep(1e6)

    except (KeyboardInterrupt, SystemExit):
        print("User cancelled process")
        raise
    except:
         print("Something went wrong")
    finally:
         GPIO.cleanup()
         ser.close()
