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

config = {
  "apiKey": "apiKey",
  "authDomain": "smartsafetyhardhat.firebaseapp.com",
  "databaseURL": "https://smartsafetyhardhat.firebaseio.com",
  "storageBucket": "smartsafetyhardhat.appspot.com"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

ser = serial.Serial("/dev/ttyS0",115200,timeout=3)  #   FONA Serial

GPIO.setmode(GPIO.BOARD)
# Setting up GPIO
# input buttons
btn_camera = 33
btn_phone = 31
btn_loghaz = 29
btn_shutdown = 35
pin_magsensor = 37

# output pins
pin_laser = 22
pin_warnleds = 24
pin_buzzer = 26

GPIO.setup([btn_camera, btn_phone, btn_loghaz, btn_shutdown, pin_magsensor], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup([pin_laser, pin_warnleds, pin_buzzer], GPIO.OUT, initial=0)

def sendSerCommand(command):
    if command == 'getlocation':
        ser.write("at+cgnspwr=?\n".encode())
        reply = ''
        while ser.inWaiting():
            reply = reply + con.read(1)
        return reply

def readUntilOK():
    reply=''
    while True:
        x = con.readline()
        reply += x
        if x == 'OK\r\n':
            return reply

# while True:
#     x = raw_input("At command: ")
#     if x.strip() == 'q':
#         break
#     reply = sendAtCommand(x)
#     print(reply)
#
#
# con.close()


def cap_image():
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

def phone_call():
    print("Phone")

def hazard_log():
    print("Hazard")
    if ser.write("AT+CGNSPWR=?".encode()) == 'OK':
        gpsLocation = ser.write("AT+CGNSINF\r\n".encode())
        gpsLatLon = gpsLocation.split(',')

        print(gpsLatLon[3],gpsLatLon[4],gpsLatLon[2])

def shutdown():
    os.system("sudo shutdown -h 'now'")

def handle(pin):
    t = None
    if pin == btn_camera:
        print("Camera Handle")
        cap_image()
    elif pin == btn_phone:
        print("Phone Handle")
        inputnum=str('5618438458')
        sercommand = "ATD"+str(inputnum)+";\r\n"
        ser.write(sercommand.encode())
        phone_call()
        time.sleep(20)
        ser.write("ATH".encode())
        print('Calling now')

    elif pin == btn_loghaz:
        print("Haz Handle")
        hazard_log()

    elif pin == btn_shutdown:
        print("System is shutting down")
        shutdown()


GPIO.add_event_detect(btn_camera, GPIO.FALLING, handle, bouncetime = 2000)
GPIO.add_event_detect(btn_phone, GPIO.FALLING, handle, bouncetime = 2000)
GPIO.add_event_detect(btn_loghaz, GPIO.FALLING, handle, bouncetime = 2000)
GPIO.add_event_detect(btn_shutdown, GPIO.FALLING, handle, bouncetime = 2000)



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
