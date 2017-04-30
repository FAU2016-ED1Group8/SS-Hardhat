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
btn_camera = 7 # mv to 7
btn_phone = 3 # mv to 3
btn_loghaz = 5 # mv to 5
in_fona_ring = 12
in_fona_state = 16
# output pins
pin_laser = 11 # mv to 11
pin_buzzer = 23



GPIO.setup([btn_camera, btn_phone, btn_loghaz, in_fona_ring, in_fona_state], GPIO.IN)
GPIO.setup([pin_laser, pin_buzzer], GPIO.OUT, initial=0)

def read_serial():
    response = []
    print("inside read serial")
    while True:
        print("inside read serial - while")
        line = ser.readline()
        print(line)
        if not line.strip():  # evaluates to true when an "empty" line is received
            print("inside read serial - blank line")
            pass
        else:
            response.append(line)
            print("line: $s" % line)
        return response

def check_gps_power():
    checkGPS_write = ser.write("AT+CGNSPWR?".encode())
    time.sleep(.3)
    gpsPwrResponse = read_serial()
    for line in gpsPwrResponse:
        print(line)
        if line == "+CGNSPWR: 0":
            print(line)
            ser.write("AT+CGNSPWR=1".encode())
            time.sleep(.3)
            check_gps_power()
        elif line == "+CGNSPWR: 1":
            print("GPS in ON")
            return True

def hazard_log():
    print("Hazard")
    check_gps_power()
    # gpsLatLon = []
    gpsLocation_write = ser.write("AT+CGNSINF\r\n".encode())
    for line in read_serial():
        print(line)
        if line == "OK":

            time.sleep(1)
            gpsResponse = read_serial()
            gpsLatLon = split
            latitude = gpsLatLon[3]
            longitude = gpsLatLon[4]


    # print(gpsLatLon[3],gpsLatLon[4],gpsLatLon[2]
    now = dt.now()
    time = now.strftime('%A %B %d, %Y %I:%M:%S %p')

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

    #hazard_string = str(record_audio())
    hazard_string = str("hello this is a test")

    #loop that will write the report to firebase (it will write to a specific node in the database)
    for p in k:
        if vincenty(loc_of_report, p).miles <= 2:                               #does the compare and the radius of 2 miles
                    print(k.index(p))                                               #prints the index of the subsation
                    data = {"hazardreport": hazard_string, "date": time}         #variable that will be written to the database
                    db.child("substation"+str(k.index(p))+"hazards").push(data)     #writes to the correct node to the database
        else:
                    print("no match")


hazard_log()
