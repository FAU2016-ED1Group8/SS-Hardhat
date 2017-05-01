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
# def sendSerCommand(command):
#     if command == 'getlocation':
#         ser.write("at+cgnspwr=?\n".encode())
#         reply = ''
#         while ser.inWaiting():
#             reply = reply + con.read(1)
#         return reply

def read_serial():
    response = []
    while True:
        line = ser.readline()
        if not line.strip():  # evaluates to true when an "empty" line is received
            pass
        else:
            response.append(line)
        return response
#
# def readUntilOK():
#     reply=''
#     while True:
#         x = con.readline()
#         reply += x
#         if x == 'OK\r\n':
#             return reply

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
    while (btn_camera == 0):
        GPIO.output(pin_laser,1)

    now = dt.today().strftime("%Y%m%d%H%M%S")
    file_name = now + '.jpg'
    file_w_path = 'fswebcam -r 640x480 -S 3 --jpeg 50 --save /home/pi/SS-Hardhat/application_code/images/'+file_name
    os.system('fswebcam -r 640x480 -S 3 --jpeg 50 --save /home/pi/SS-Hardhat/application_code/images/'+file_name)
    print(file_w_path)

    #####################################################################
    #####################Write to Storage################################
    #####################################################################
    GPIO.output(pin_laser,0)
    print(file_name)
    storage = firebase.storage()
    #storage.child("Camera/"+"forest").put("/home/pi/Desktop/images/forest.jpg")
    storage.child("Camera/"+file_name).put("/home/pi/SS-Hardhat/application_code/images/"+file_name)

    #####################################################################
    ####################Write to Database################################
    #####################################################################
    db = firebase.database()

    #time variable
    now = dt.now()
    time = now.strftime('%A %B %d, %Y %I:%M:%S %p')
    token = None

    imageUrl = storage.child("Camera/"+file_name).get_url(token)

    #variable that will be written to the database
    data = {"ImageName":imageUrl, "date": time}
    db.child("Camera Data").push(data)


    print("success!")

def check_phone_state():
    print("Checking for dialtone")
    # if dialtone start_call()
    # inputnum=str('5618438458')
    inputnum=str('9547099911')
    start_call(inputnum)
    # elif no_dialton end_call()



def start_call(inputnum):
    print("Starting call")
    callingVar = 'ATD'+str(inputnum)+';\r\n'
    ser.write(callingVar.encode())
    print('Calling now: %d' % inputnum)

def end_call():
    print("ending call")

def record_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Say something!")
        audio = r.listen(source)

    #Speech recognition using Google Speech Recognition
    try:
        # for testing purposes, we're just using the default API key
        # to use another API key, use `r.recognize_google(audio, key="GOOGLE_SPEECH_RECOGNITION_API_KEY")`
        # instead of `r.recognize_google(audio)`
        # print("You said: " + r.recognize_google(audio))
        google_translate = r.recognize_google(audio)
        return google_translate
    except sr.UnknownValueError:
        return "Google Speech Recognition could not understand audio"
    except sr.RequestError as e:
        return "Could not request results from Google Speech Recognition service; {0}".format(e)


def voice_dial():
    #retrieves number of contacts from firebase
    num_of_contacts = list(range(len([users.key() for users in (db.child("Contact Information").get()).each()])))


    #gets the first name/last name/number of each person in the contacts from firebase
    first_name = [(db.child("Contact Information").child(str(x)).child("First").get()).val() for x in num_of_contacts ]
    last_name = [(db.child("Contact Information").child(str(x)).child("Last").get()).val() for x in num_of_contacts ]
    phone_num = [(db.child("Contact Information").child(str(x)).child("Number").get()).val() for x in num_of_contacts ]

    ## Send Beep ## TODO

    call_string = str(record_audio())

    #variable that holds the first/last names of the people in the contact list
    k =  list (zip(first_name, last_name))

    #joins the first/last names of the people in the contact list
    complete_names = [(' '.join(j)) for j in k]

    #removes "(", ")","-" from the phone numbers retrieved from firebase
    sanitized_phone_numbers = [int(''.join(c for c in x if c.isdigit())) for x in phone_num]

    #performs the string compare using fuzzywuzzy module
    string_compare = process.extractOne(call_string, complete_names, scorer = fuzz.partial_ratio)

    #variable that holds the name of the string match
    name_match = str((string_compare)[0])

    #phone and name directory of the contact list in firebase
    phone_directory =  dict (zip(complete_names, sanitized_phone_numbers))

    #variable that holds the number to be dialed
    phone_string = str(phone_directory.get(name_match))

    return(phone_string)

def check_gps_power():
    checkGPS_write = ser.write("AT+CGNSPWR?".encode())
    time.sleep(.3)
    gpsPwrResponse = read_serial()
    for line in gpsPwrResponse:
        if line == "+CGNSPWR: 0":
            ser.write("AT+CGNSPWR=1".encode())
            time.sleep(.3)
            check_gps_power()
        elif line == "+CGNSPWR: 1":
            return 1
def hazard_log():
    print("Hazard")
    if check_gps_power():
    # gpsLatLon = []
        for line in read_serial():
            if line == "OK":
                gpsLocation_write = ser.write("AT+CGNSINF\r\n".encode())
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

        hazard_string = str(record_audio())
        #hazard_string = str("hello this is a test")

        #loop that will write the report to firebase (it will write to a specific node in the database)
        for p in k:
            if vincenty(loc_of_report, p).miles <= 2:                               #does the compare and the radius of 2 miles
                        print(k.index(p))                                               #prints the index of the subsation
                        data = {"hazardreport": hazard_string, "date": time}         #variable that will be written to the database
                        db.child("substation"+str(k.index(p))+"hazards").push(data)     #writes to the correct node to the database
            else:
                        print("no match")                                               #have to do something else in the future. Not known yet.

def handle(pin):
    t = None
    if pin==btn_camera and GPIO.input(btn_camera):
        print("Camera Handle")
        cap_image()
    elif pin==btn_camera and (GPIO.input(btn_camera) == False):
        print("Laser on")
        GPIO.output(pin_laser,GPIO.HIGH)


    elif pin == btn_phone:
        print("Phone Handle")
        # phone_call()
        check_phone_state()

    elif pin == btn_loghaz:
        print("Haz Handle")
        hazard_log()

GPIO.add_event_detect(btn_camera, GPIO.BOTH, handle, bouncetime = 20)
GPIO.add_event_detect(btn_phone, GPIO.FALLING, handle, bouncetime = 2000)
GPIO.add_event_detect(btn_loghaz, GPIO.FALLING, handle, bouncetime = 2000)



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
