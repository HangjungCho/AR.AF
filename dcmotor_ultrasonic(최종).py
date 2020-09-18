import RPi.GPIO as GPIO
import time
from threading import Thread
import threading


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Ultrasonic
trig = 0
echo = 1
GPIO.setup(trig, GPIO.OUT)
GPIO.setup(echo, GPIO.IN) # Peri v 2.1


#모터
MOTOR_P = 4
MOTOR_N = 25
MOTOR_EN = 12
GPIO.setup(MOTOR_P, GPIO.OUT)
GPIO.setup(MOTOR_N, GPIO.OUT)
GPIO.setup(MOTOR_EN, GPIO.OUT)

distance = 0

def ultrasonic_func():
    while True:
        global distance

        GPIO.output(trig, False)
        time.sleep(0.5)

        GPIO.output(trig, True)
        time.sleep(0.00001)
        GPIO.output(trig, False)

        while GPIO.input(echo) == False: # Peri v 2.1
        #while GPIO.input(echo) == True : # Peri v 2.0
            pluse_start = time.time()

        while GPIO.input(echo) == True:
        #while GPIO.input(echo) == False : # Peri v 2.0
            pluse_end = time.time()

        pluse_duration = pluse_end - pluse_start
        distance = pluse_duration * 17000
        distance = round(distance,2)

        print('Distance : {:.2f}cm'.format(distance))

def dcmotor_func():
    while True:
        global distance

        if distance <= 100.00:
            print('stop')
            GPIO.output(MOTOR_P, False)
            GPIO.output(MOTOR_EN, False)
        else:
            print('forword' )
            GPIO.output(MOTOR_P, True)
            GPIO.output(MOTOR_N, False)
            GPIO.output(MOTOR_EN, True)
            print('Server Distance : {:.2f}cm'.format(distance))
            time.sleep(1)

if __name__ == '__main__':
    p = Thread(target = ultrasonic_func, args=())
    p.start() #프로세스생성
    
    p2= Thread(target = dcmotor_func, args=())
    p2.start() #프로세스생성
    
    p.join()
    p2.join()
    
    print('stop parent process', end='')

