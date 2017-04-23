import RPi.GPIO as GPIO


ser = serial.Serial("/dev/ttyS0",115200,timeout=3)  #   FONA Serial
GPIO.setmode(GPIO.BOARD)

btn_camera = 37

GPIO.setup(btn_camera, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


def handle(pin):
    if pin == btn_phone:
        print("Phone Handle")
        startCall()


def startCall():
    print("insideStartCall")
    inputnum=str('5618438458')
    ser.write("ATD"+str(inputnum)+";\r")

GPIO.add_event_detect(btn_phone, GPIO.FALLING, handle)

while True:
	time.sleep(1e6)    
