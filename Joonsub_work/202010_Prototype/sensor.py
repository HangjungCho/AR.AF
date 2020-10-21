import RPi.GPIO as GPIO 
import sys
import time

sensor = 18

GPIO.setmode(GPIO.BCM)

GPIO.setup(motor, GPIO.IN)

try:
    while 1:
        if GPIO.input(motor) == 0:
            print('제품감지됨')
            time.sleep(1)
        else:
            print('제품감지중')
            time.sleep(1)
except KeyboardInterrupt as e:
    GPIO.cleanup()
    sys.exit()

GPIO.cleanup()