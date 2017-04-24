import RPi.GPIO as GPIO
import time
import threading
from subprocess import call
import serial

ser = serial.Serial("/dev/ttyS0",115200,timeout=3)  #   FONA Serial
GPIO.setmode(GPIO.BOARD)

# Setting up GPIO

# input buttons
btn_camera = 37
btn_phone = 35
btn_loghaz = 33
btn_shutdown = 31
pin_magsensor = 29

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
    # call(["python3 capture_image.py"])
    print("Camera")

def phone_call():
    print("Phone")

def hazard_log():
    print("Hazard")
    if ser.write("AT+CGNSPWR=?".encode()) == 'OK':
        gpsLocation = ser.write("AT+CGNSINF\r\n".encode())
        gpsLatLon = gpsLocation.split(',')

        print(gpsLatLon[3],gpsLatLon[4],gpsLatLon[2])

def handle(pin):
    t = None
    if pin == btn_camera:
        print("Camera Handle")
        cap_image()
    elif pin == btn_phone:
        print("Phone Handle")
        inputnum=str('5618438440')
        sercommand = "ATD"+str(inputnum)+";\r\n"
        ser.write(sercommand.encode())
        phone_call()
        print('Calling now')

    elif pin == btn_loghaz:
        print("Haz Handle")
        hazard_log()



GPIO.add_event_detect(btn_camera, GPIO.FALLING, handle)
GPIO.add_event_detect(btn_phone, GPIO.FALLING, handle)
GPIO.add_event_detect(btn_loghaz, GPIO.FALLING, handle)




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
