import socket
import datetime
from datetime import datetime as dt
from pyrebase import pyrebase           #pyrebase library

#sets up firebase
config = {
  "apiKey": "apiKey",
  "authDomain": "smartsafetyhardhat.firebaseapp.com",
  "databaseURL": "https://smartsafetyhardhat.firebaseio.com",
  "storageBucket": "smartsafetyhardhat.appspot.com"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

#gets hostname
hostname = socket.gethostname()

#GPS Coordinates (DUMMY VALUES)
gps_coordinates = "26.43212, -80.2324"

#parse Coordinates to longitude and latitude
lat = gps_coordinates.split(",")[0]
long = (gps_coordinates.split(",")[1]).lstrip()


#time variable
now = datetime.datetime.now()
time = now.strftime('%A %B %d, %Y %I:%M:%S %p')


#variable that will be written to the database
GPS_data = {"GPSUserID":hostname, "GPSdate": time, "lat": lat, "long": long}                 
db.child("User GPS Data").push(GPS_data)

#success statement
print("success")
