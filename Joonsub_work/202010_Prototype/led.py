import RPi.GPIO as GPIO 

import time

GPIO.setmode(GPIO.BCM)

GPIO.setup(17, GPIO.OUT)
GPIO.setup(27, GPIO.OUT)
GPIO.setup(22, GPIO.OUT)


GPIO.output(17,True)

time.sleep(3)

GPIO.output(17, False)

GPIO.output(27,True)

time.sleep(3)

GPIO.output(27, False)

GPIO.output(22,True)

time.sleep(3)

GPIO.output(22, False)

GPIO.cleanup()