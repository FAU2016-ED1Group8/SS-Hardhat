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
    if GPIO.input(btn_camera):
        print("Camera Handle")
        cap_image()
    elif (GPIO.input(btn_camera) == False):
        GPIO.output(pin_laser,1)

def cap_image():
    GPIO.output(pin_laser,0)
    print("CLICK!")



GPIO.add_event_detect(btn_camera, GPIO.BOTH, laser_on, bouncetime = 2000)


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
