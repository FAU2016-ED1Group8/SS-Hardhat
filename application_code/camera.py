import os
import datetime
from datetime import datetime as dt

import speech_recognition as sr
import datetime                         #time library
from pyrebase import pyrebase           #pyrebase library

#sets up firebase
config = {
  "apiKey": "apiKey",
  "authDomain": "smartsafetyhardhat.firebaseapp.com",
  "databaseURL": "https://smartsafetyhardhat.firebaseio.com",
  "storageBucket": "smartsafetyhardhat.appspot.com"
}

#call(["fswebcam" -r 640x480 --save image4.jpg])
#print("image4 captured")
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
