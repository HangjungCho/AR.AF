import RPi.GPIO as GPIO 

import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(25, GPIO.OUT)

GPIO.output(25,False)

time.sleep(3)

GPIO.output(25, True)

GPIO.cleanup()