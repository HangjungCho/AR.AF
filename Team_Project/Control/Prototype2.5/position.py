
from multiprocessing import Process, Queue
from threading import Thread

import socket
import cv2
import numpy as np
import time, datetime
import sys
import os
import RPi.GPIO as GPIO

# Machine Process global variations
Check1 = 0
Check2 = 0
Check3 = 0


# Cam Process global variations
ircheck = 0

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)







class Conveyor_main(Thread):
    def __init__(self):
        Thread.__init__(self, name='Conveyor_main')
        self.con1_port = 5 # 29
        self.con2_port = 6 # 31

        GPIO.setup(self.con1_port, GPIO.OUT)
        GPIO.setup(self.con2_port, GPIO.OUT)

    def __del__( self ):
        print( "Closing Conveyor_main" )

    def conveyor_init(self):
        GPIO.output(self.con1_port, True)
        GPIO.output(self.con2_port, True)

    def main_conveyor_On(self):
        GPIO.output(self.con1_port, False)
        GPIO.output(self.con2_port, False)
        
    def main_conveyor_Off(self):
        GPIO.output(self.con1_port, True)
        GPIO.output(self.con2_port, True)

    def run(self):
        global Check2, Check3
        self.conveyor_init()
        while True:
            if (Check2 or Check3) == 1 :
                self.main_conveyor_Off()
                time.sleep(3.5)
            else:
                self.main_conveyor_On()



class Conveyor1(Thread):
    def __init__(self):
        Thread.__init__(self, name='Conveyor1')
        self.con3_port = 13 # 33
        GPIO.setup(self.con3_port, GPIO.OUT)

    def __del__( self ):
        print( "Closing Conveyor1" )

    def conveyor_init(self):
        GPIO.output(self.con3_port, True)

    def con1_On(self):
        GPIO.output(self.con3_port, False)

    def con1_Off(self):
        GPIO.output(self.con3_port, True)

    def run(self):
        global Check2
        self.conveyor_init()
        while True:
            if Check2 == 1:
                self.con1_On()
                time.sleep(7)
            elif Check2 == 0:
                self.con1_Off()



class Conveyor2(Thread):
    def __init__(self):
        Thread.__init__(self, name='Conveyor2')
        self.con4_port = 19 # 35
        GPIO.setup(self.con4_port, GPIO.OUT)

    def __del__( self ):
        print( "Closing Conveyor2" )

    def conveyor_init(self):
        GPIO.output(self.con4_port, True)

    def con2_On(self):
        GPIO.output(self.con4_port, False)

    def con2_Off(self):
        GPIO.output(self.con4_port, True)

    def run(self):
        global Check3
        self.conveyor_init()
        while True:
            if Check3 == 1:
                self.con2_On()
                time.sleep(7)
            elif Check3 == 0:
                self.con2_Off()



class PushMotor1(Thread):
    def __init__(self):
        Thread.__init__(self, name='PushMotor1')
        self.ports = 23 # 16
        GPIO.setup(self.ports, GPIO.OUT)

    def __del__( self ):
        print( "Closing PushMotor1" )

    def push_activate1(self):
        GPIO.output(self.ports, False)
        time.sleep(5.7)
        GPIO.output(self.ports, True)
    
    def push_deactivate1(self):
        GPIO.output(self.ports, True)
    
    def run(self):
        global Check2
        while True:
            if Check2 == 1:
                self.push_activate1()
                Check2 = 0
                print('PushMotor1 is On')
            else:
                self.push_deactivate1()



class PushMotor2(Thread):
    def __init__(self):
        Thread.__init__(self, name='PushMotor2')
        self.ports = 24 # 18
        GPIO.setup(self.ports, GPIO.OUT)

    def __del__( self ):
        print( "Closing PushMotor2" )

    def push_activate2(self):
        GPIO.output(self.ports, False)
        time.sleep(5.7)
        GPIO.output(self.ports, True)

    def push_deactivate2(self):
        GPIO.output(self.ports, True)
    
    def run(self):
        global Check3
        while True:
            if Check3==1:
                self.push_activate2()
                print('PushMotor2 is On')
                Check3 = 0
                
            else:
                self.push_deactivate2()



class IRSensor1(Thread):
    def __init__(self):
        Thread.__init__(self, name='IRSensor1')
        self.port = 16 # 36
        GPIO.setup(self.port, GPIO.IN)

    def __del__( self ):
        print( "Closing IRSensor1" )

    def run(self):
        global Check1
        while True:
            if GPIO.input(self.port) == 0:
                Check1 = 1
                time.sleep(1)
            else:
                Check1 = 0 



class IRSensor2(Thread):
    def __init__(self):
        Thread.__init__(self, name='IRSensor2')

        self.port = 21 # 40
        GPIO.setup(self.port, GPIO.IN)

    def __del__( self ):
        print( "Closing IRSensor2" )

    def run(self):
        global Check2
        while True:
            if GPIO.input(self.port) == 0:
                Check2 = 1 # if Check type is 'A', PushMotor1 is On
                time.sleep(1)
            else:
                Check2 = 0
            



class IRSensor3(Thread):
    def __init__(self):
        Thread.__init__(self, name='IRSensor3')

        self.port = 20 # 38
        GPIO.setup(self.port, GPIO.IN)

    def __del__( self ):
        print( "Closing IRSensor3" )

    def run(self):
        global Check3
        while True:
            if GPIO.input(self.port) == 0:
                Check3 = 1
                time.sleep(1)
            else:
                Check3 = 0
            

class TurnOff(Conveyor_main, Conveyor1, Conveyor2, PushMotor1, PushMotor2):
    def __init__(self):
        Conveyor_main.__init__(self)
        Conveyor1.__init__(self)
        Conveyor2.__init__(self)
        PushMotor1.__init__(self)
        PushMotor2.__init__(self)
    def __del__(self):
        print('Turn Off All Motor')

    def AllOff(self):
        self.main_conveyor_Off()
        self.con1_Off()
        self.con2_Off()
        self.push_deactivate1()
        self.push_deactivate2()
        


class MachineProcess( Process, TurnOff ):
    def __init__( self ):


        Process.__init__( self, name = "MachineProcess" )
        TurnOff.__init__(self)
        print( '[MachineProcess __init__]' )

    def __del__( self ):
        self.AllOff()
        print( '[MachineProcess __del__]' )

    def run(self):


        # make object
        conveyor_main = Conveyor_main()
        conveyor1 = Conveyor1()
        conveyor2 = Conveyor2()
        push1 = PushMotor1()
        push2 = PushMotor2()
        IR1 = IRSensor1()
        IR2 = IRSensor2()
        IR3 = IRSensor3()

        # start
        conveyor_main.start()
        conveyor1.start()
        conveyor2.start()
        push1.start()
        push2.start()
        IR1.start()
        IR2.start()
        IR3.start()        
        


                
if __name__ == '__main__':
    server_ip = '192.168.0.125'
    server_port = 9000

    MP = MachineProcess( )
    MP.start()

            
            

