import speech_recognition as sr

import datetime                         #time library
from pyrebase import pyrebase           #pyrebase library
import geopy                            #geopy for coordinate comparison
from geopy.distance import vincenty     #geopy function for long/lat comparison
from geopy.geocoders import Nominatim

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


#sets up firebase
config = {
  "apiKey": "apiKey",
  "authDomain": "smartsafetyhardhat.firebaseapp.com",
  "databaseURL": "https://smartsafetyhardhat.firebaseio.com",
  "storageBucket": "smartsafetyhardhat.appspot.com"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

#dummy coordinates for location of hazard report
longitude = -80.208465
latitude =  26.646333

#time variable
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
