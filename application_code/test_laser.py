import RPi.GPIO as GPIO
import time
import os
from subprocess import call

GPIO.setmode(GPIO.BOARD)

btn_camera = 7 # mv to 7
pin_laser = 11 # mv to 11


GPIO.setup(btn_camera, GPIO.IN)
GPIO.setup(pin_laser, GPIO.OUT, initial=0)

def handle(pin):
    t = None
    if pin==btn_camera and GPIO.input(btn_camera):
        print("Camera Handle")
        cap_image()
    elif pin==btn_camera and (GPIO.input(btn_camera) == False):
        print("Laser on")
        GPIO.output(pin_laser,GPIO.HIGH)

def cap_image():
    GPIO.output(pin_laser,0)
    print("CLICK!")



GPIO.add_event_detect(btn_camera, GPIO.BOTH, handle, bouncetime = 20)


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

