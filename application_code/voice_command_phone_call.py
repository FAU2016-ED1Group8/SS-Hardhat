from pyrebase import pyrebase           #pyrebase library
from fuzzywuzzy import fuzz             #string compare module
from fuzzywuzzy import process
import speech_recognition as sr


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

#retrieves number of contacts from firebase
num_of_contacts = list(range(len([users.key() for users in (db.child("Contact Information").get()).each()])))


#gets the first name/last name/number of each person in the contacts from firebase
first_name = [(db.child("Contact Information").child(str(x)).child("First").get()).val() for x in num_of_contacts ]
last_name = [(db.child("Contact Information").child(str(x)).child("Last").get()).val() for x in num_of_contacts ]
phone_num = [(db.child("Contact Information").child(str(x)).child("Number").get()).val() for x in num_of_contacts ]

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

print(phone_string)

