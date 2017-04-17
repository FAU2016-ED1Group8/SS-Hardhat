import RPi.GPIO as GPIO
import time
import threading
from subprocess import call

GPIO.setmode(GPIO.BOARD)

# Setting up GPIO

# input buttons
btn_camera = 29
btn_phone = 31
btn_loghaz = 33
btn_shutdown = 35
pin_magsensor = 37

# output pins
pin_laser = 22
pin_warnleds = 24
pin_buzzer = 26

GPIO.setup([btn_camera, btn_phone, btn_loghaz, btn_shutdown, pin_magsensor], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup([pin_laser, pin_warnleds, pin_buzzer], GPIO.OUT, initial.GPIO.LOW)

def cap_image():
    # call(["python3 capture_image.py"])
    print("Camera")

def phone_call():
    print("Phone")

def hazard_log():
    print("Hazard")

def handle(pin):
    t = None
    if pin == btn_camera:
        cap_image()
    else if pin == btn_phone:
        phone_call()
    else if pin == btn_loghaz:
        hazard_log()



GPIO.add_event_detect(btn_camera, GPIO.FALLING, handle)
GPIO.add_event_detect(btn_camera, GPIO.FALLING, handle)
GPIO.add_event_detect(btn_camera, GPIO.FALLING, handle)




while True:
	time.sleep(1e6)
