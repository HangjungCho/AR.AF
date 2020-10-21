# import tensorflow as tf
# import cv2
import numpy as np 
import math
import socket
import time, datetime
# from tensorflow.keras.models import load_model
from multiprocessing import Process
from threading import Thread
import sys
import os
import RPi.GPIO as GPIO

item_list = []
Check1 = 0
Check2 = 0
Check3 = 0


class NetClient():
    def __init__( self, hostIP, hostPort ):
        self.host = hostIP
        self.port = hostPort

        self.sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.server_address = ( self.host, self.port )
        self.sock.connect( self.server_address )

    def __del__( self ):
        self.sock.close()
        print( "Closing connection to the server" )

    def sendData( self, data ):
        try:
            print( "Sending --> {0}".format( data ) )
            self.sock.send( data.encode() )

        except socket.errno as e:
            print( "Socket error: %s" %str(e) )
        except Exception as e:
            print( "Other exception: %s" %str(e) )

class Con1(Thread):
    def __init__(self):
        Thread.__init__(self, name='Con1')
        self.ports = 6
        GPIO.setup(self.ports, GPIO.OUT)

    def __del__( self ):
        print( "Closing Con1" )

    def run(self):
        GPIO.output(self.ports,False)
        time.sleep(5)
        GPIO.output(self.ports,True)

class Con2(Thread):
    def __init__(self):
        Thread.__init__(self, name='Con2')
        self.ports = 13
        GPIO.setup(self.ports, GPIO.OUT)

    def __del__( self ):
        print( "Closing Con2" )

    def run(self):
        GPIO.output(self.ports,False)
        time.sleep(5)
        GPIO.output(self.ports,True)

class DischargeMotor1(Thread):
    def __init__(self):
        Thread.__init__(self, name='DischargeMotor1')
        self.ports = 19
        GPIO.setup(self.ports, GPIO.OUT)

    def __del__( self ):
        print( "Closing DischargeMotor1" )

    def run(self):
        time.sleep(5.1)
        GPIO.output(self.ports,False)
        time.sleep(5.9)
        GPIO.output(self.ports,True)

class DischargeMotor2(Thread):
    def __init__(self):
        Thread.__init__(self, name='DischargeMotor2')
        self.ports = 26
        GPIO.setup(self.ports, GPIO.OUT)

    def __del__( self ):
        print( "Closing DischargeMotor1" )

    def run(self):
        time.sleep(5.1)
        GPIO.output(self.ports,False)
        time.sleep(5.9)
        GPIO.output(self.ports,True)

class InfraerdSensor1(Thread):
    def __init__(self):
        Thread.__init__(self, name='InfraerdSensor1')
        self.ports = 18
        GPIO.setup(self.ports, GPIO.IN)

    def __del__( self ):
        print( "Closing InfraerdSensor1" )

    def run(self):
        try:
            while 1:
                global Check1
                if GPIO.input(self.ports) == 0:
                    Check1 = 1
                    time.sleep(2.2)
                else:
                    Check1 = 0
                    time.sleep(0.1)
        except KeyboardInterrupt:
            GPIO.cleanup()
            sys.exit()


# class InfraerdSensor2(Thread):
#     def __init__(self):
#         Thread.__init__(self, name='InfraerdSensor2')
#         self.ports = 7
#         GPIO.setup(self.ports, GPIO.IN)

#     def __del__( self ):
#         print( "Closing InfraerdSensor2" )

#     def run(self):
#         try:
#             while 1:
#                 global Check1
#                 if GPIO.input(self.ports) == 0:
#                     Check2 = 1
#                     time.sleep(1)
#                 else:
#                     Check2 = 0
#                     time.sleep(1)

# class InfraerdSensor3(Thread):
#     def __init__(self):
#         Thread.__init__(self, name='InfraerdSensor3')
#         self.ports = 8
#         GPIO.setup(self.ports, GPIO.IN)

#     def __del__( self ):
#         print( "Closing InfraerdSensor3" )

#     def run(self):
#         try:
#             while 1:
#                 global Check3
#                 if GPIO.input(self.ports) == 0:
#                     Check3 = 1
#                     time.sleep(1)
#                 else:
#                     Check3 = 0
#                     time.sleep(1)


# class RelayModuleThread1(Thread):
#     def __init__(self):
#         Thread.__init__(self, name='RelayModuleThread1')
#         self.ports = (9)
#         self.direction = ( 'RelayModule1' )
#         self.relay = RelayModule( self.ports, self.direction )

#     def __del__( self ):
#         print( "Closing RelayModuleThread1" )

#     def run(self):
#             while True:
#                 global Check1
#                 global item_list
#                 if Check1 == 1:
#                     try:
#                         if item_list[0] != 1:
#                             self.relay.RelayModule_on()
#                             time.sleep(10)
#                             self.relay.RelayModule_off()
#                             item_list.pop(0)                        
#                         elif item_list[1] != 1:
#                             self.relay.RelayModule_on()
#                             time.sleep(10)
#                             self.relay.RelayModule_off()
#                             item_list.pop(1)
#                         else:
#                             pass
#                     except:
#                         continue

# class RelayModuleThread2(Thread):
#     def __init__(self):
#         Thread.__init__(self, name='RelayModuleThread1')
#         self.ports = (10)
#         self.direction = ( 'RelayModule2' )
#         self.relay = RelayModule( self.ports, self.direction )

#     def __del__( self ):
#         print( "Closing RelayModuleThread2" )

#     def run(self):
#             while True:
#                 global Check2
#                 global item_list
#                 if Check2 == 1:
#                     try:
#                         if item_list[0] == 2:
#                             self.relay.RelayModule_on()
#                             time.sleep(10)
#                             self.relay.RelayModule_off()
#                             item_list.pop(0)                        
#                         else:
#                             item_list.pop(0)
#                     except:
#                         continue

# class Cam(Thread):
#     def __init__(self, hostIP, hostPort):
#         Thread.__init__(self, name='Cam')
#         self.host = hostIP
#         self.port = hostPort

#     def __del__( self ):
#         print( "Closing Cam" )
#         sys.exit()

#     def flatten_process(self, img_input):
#         gray = cv2.cvtColor(img_input, cv2.COLOR_BGR2GRAY)
#         gray = cv2.resize(gray, (28, 28), interpolation=cv2.INTER_AREA)
#         (thresh, img_binary) = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)

#         h,w = img_binary.shape

#         ratio = 100/h
#         new_h = 100
#         new_w = w * ratio

#         img_empty = np.zeros((110,110), dtype=img_binary.dtype)
#         img_binary = cv2.resize(img_binary, (int(new_w), int(new_h)), interpolation=cv2.INTER_AREA)
#         img_empty[:img_binary.shape[0], :img_binary.shape[1]] = img_binary

#         img_binary = img_empty
#         cnts = cv2.findContours(img_binary.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#         # 컨투어의 무게중심 좌표를 구합니다. 
#         M = cv2.moments(cnts[0][0])
#         center_x = (M["m10"] / M["m00"])
#         center_y = (M["m01"] / M["m00"])

#         # 무게 중심이 이미지 중심으로 오도록 이동시킵니다. 
#         height,width = img_binary.shape[:2]
#         shiftx = width/2-center_x
#         shifty = height/2-center_y
#         Translation_Matrix = np.float32([[1, 0, shiftx],[0, 1, shifty]])
#         img_binary = cv2.warpAffine(img_binary, Translation_Matrix, (width,height))
#         img_binary = cv2.resize(img_binary, (28, 28), interpolation=cv2.INTER_AREA)
#         flatten = img_binary.flatten() / 255.0
#         return flatten

#     def run(self):
#         print('start')
#         global item_list
#         try:
#             loop = True
#             # print('start2')
#             cap = cv2.VideoCapture(0)
#             width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
#             height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

#             model = load_model('04-0.0781.hdf5')  

#             while loop:
#                 # print('start3')
#                 ret, img_color = cap.read()

#                 if ret == False:
#                     print('ret error')
#                     break

#                 img_input = img_color.copy()
#                 cv2.rectangle(img_color, (250, 150),  (width-250, height-150), (0, 0, 255), 3)
#                 cv2.imshow('bgr', img_color)

#                 img_roi = img_input[150:height-150, 250:width-250]


#                 key = cv2.waitKey(1)
#                 try:
#                     if key == 27:
#                         # self.sendData('END')
#                         global a
#                         a = 2
#                         break
                    
#                     elif key == 32:
#                         flatten = self.flatten_process(img_roi)
        
#                         predictions = model.predict(flatten[np.newaxis,:])

#                         with tf.compat.v1.Session() as sess:
#                             print(tf.argmax(predictions, 1).eval())

#                         now = datetime.datetime.now()
#                         Capturedate = now.strftime( '%Y-%m-%d' )
#                         Capturetime = now.strftime( '%H:%M:%S' )
#                         cal = 'ADD'
#                         data = (str(tf.argmax(predictions,1)))[11:12]
#                         print(data)
                        
#                         cv2.imshow('img_roi', img_roi)
#                         item_list.append(data)
#                         product = data+cal+Capturedate+Capturetime
#                         print(item_list)
#                         print(product)
#                         # self.sendData(product)
#                         NC = NetClient(self.host, self.port)
#                         NC.sendData(product)

#                 except ZeroDivisionError:
#                     print('ZeroDivisionError')
#                     continue

#             cap.release()
#             cv2.destroyAllWindows()
#         except ( RuntimeError):
#             print("RuntimeError")
#         except KeyboardInterrupt as e:
#             print(e)
#             sys.exit()


class MachineProcess( Process, NetClient):#, Cam):
    def __init__( self,  host, port):
        self.host = host
        self.port = port
        Process.__init__( self, name = "MachineProcess" )
        # NetClient.__init__( self, host, port )
        # Cam.__init__( self, host, port )
        print( '[MachineProcess __init__]' )

    def __del__( self ):
        GPIO.cleanup()
        print( '[MachineProcess __del__]' )

    def run(self):
        GPIO.setmode(GPIO.BCM)
        # cam = Cam(self.host,self.port)
        MC1 = Con1()
        MC2 = Con2()
        DC1 = DischargeMotor1()
        DC2 = DischargeMotor2()
        IS1 = InfraerdSensor1()
        # cam.start()
        MC1.start()
        MC2.start()
        DC1.start()
        DC2.start()
        IS1.start()

if __name__ == '__main__':
    server_ip = '192.168.0.84'
    server_port = 9000
    sensorClientProcess = MachineProcess( server_ip, server_port )
    sensorClientProcess.start()



