# from tensorflow.keras.models import load_model
from multiprocessing import Process, Queue, Event
from threading import Thread
from PIL import Image, ImageOps

# import tensorflow as tf
import socket
import cv2
import numpy as np
import time, datetime
import sys
import os
import RPi.GPIO as GPIO

from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
import threading

# Machine Process global variations
Check1 = 0
Check2 = 0
Check3 = 0


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

class NetFunc():
    def __init__( self, hostIP, hostPort ):
        self.host = hostIP
        self.port = hostPort
        self.client_sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.server_address = ( self.host, self.port )
        self.client_sock.connect((self.host, self.port) )

    def __del__( self ):
        self.client_sock.close()
        print( "Closing connection to the server" )

    def sendData( self, stringData ):
        try:
            self.client_sock.send(str(len(stringData)).ljust(28).encode())
            self.client_sock.send(stringData)

        except socket.errno as e:
            print( "Socket error: %s" %str(e) )
        except ConnectionResetError as e:
            print( "ConnectionResetError: %s" %str(e) )
        except Exception as e:
            print( "Other exception: %s" %str(e) )
        
    def receiveData( self ):
        return self.client_sock.recv(1024)


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
                time.sleep(2)
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
                time.sleep(8)
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
                time.sleep(8) 
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
        time.sleep(5.73)
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
        time.sleep(5.73)
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
    def __init__(self, M2Cque, C2Mque):
        Thread.__init__(self, name='IRSensor1')
        self.port = 16 # 36

        self.C2Mque = C2Mque
        self.M2Cque = M2Cque
        GPIO.setup(self.port, GPIO.IN)

    def __del__( self ):
        print( "Closing IRSensor1" )

    def run(self):
        global Check1
        while True:
            if GPIO.input(self.port) == 0:
                Check1 = 1
                self.M2Cque.put(Check1,timeout=1)
                print('active Put')
                time.sleep(2)
                Check1 = 0                
            else:
                Check1 = 0 
                print('run ok')
                time.sleep(1)



class IRSensor2(Thread):
    def __init__(self, C2Mque, item_list):
        Thread.__init__(self, name='IRSensor2')

        self.port = 21 # 40
        self.C2Mque = C2Mque
        self.item_list = item_list
        GPIO.setup(self.port, GPIO.IN)

    def __del__( self ):
        print( "Closing IRSensor2" )

    def run(self):
        global Check2
        while True:
            if GPIO.input(self.port) == 0:
                if self.C2Mque.qsize() == 0:
                    continue
                else:
                    Check_type = self.C2Mque.get(timeout=100) # get Output value from Queue( Camera to Machine )
                    print('CheckType : {}'.format(Check_type)) # just test code
                    if Check_type == 'A':
                        Check2 = 1 # if Check type is 'A', PushMotor1 is On
                        print('Type A Sensed')
                        
                    else:
                        self.item_list.put(Check_type,timeout=1) # B or C case
                        print('Not Type A')
                        Check2 = 0
            else:
                Check2 = 0
            time.sleep(1)



class IRSensor3(Thread):
    def __init__(self, C2Mque, item_list):
        Thread.__init__(self, name='IRSensor3')

        self.port = 20 # 38
        self.C2Mque = C2Mque
        self.item_list = item_list
        GPIO.setup(self.port, GPIO.IN)

    def __del__( self ):
        print( "Closing IRSensor3" )

    def run(self):
        global Check3
        while True:
            if GPIO.input(self.port) == 0:

                if self.item_list.qsize() == 0:
                    continue
                else:
                    Check_type = self.item_list.get(timeout=100)
                    print('CheckType : {}'.format(Check_type)) # just test code
                    print('New Check3 : {}'.format(Check3))
                    if Check_type == 'B':
                        Check3 = 1
                        print('Type B Sensed')
                    elif Check_type == 'C':
                        Check3 = 0
                        print('Type C Sensed')
                    else:
                        Check3 = 0
                        print('Error Type Sensed')

            else:
                Check3 = 0
            time.sleep(1)

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
    def __init__( self, M2Cque, C2Mque):

        self.M2Cque = M2Cque
        self.C2Mque = C2Mque
        self.item_list = Queue()
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
        IR1 = IRSensor1(self.M2Cque, self.C2Mque)
        IR2 = IRSensor2(self.C2Mque, self.item_list)
        IR3 = IRSensor3(self.C2Mque, self.item_list)

        # thread start
        conveyor_main.start()
        conveyor1.start()
        conveyor2.start()
        # push1.start()
        # push2.start()
        IR1.start()
        # IR2.start()
        # IR3.start()        
        



class CameraProcess( Process, NetFunc):
    def __init__( self, host, port, M2Cque, C2Mque):
        Process.__init__(self, name='CameraProcess')
        NetFunc.__init__( self, host, port )
        
        self.M2Cque = M2Cque
        self.C2Mque = C2Mque
        print( '[CameraProcess __init__]' )

    def __del__( self ):
        print( '[CameraProcess __del__]' )




class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(750, 540)
        self.btn_1 = QtWidgets.QPushButton(Dialog)
        self.btn_1.setGeometry(QtCore.QRect(510, 450, 105, 30))
        self.btn_1.setObjectName("btn_1")
        self.btn_2 = QtWidgets.QPushButton(Dialog)
        self.btn_2.setGeometry(QtCore.QRect(635, 450, 105, 30))
        self.btn_2.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.btn_2.setObjectName("btn_2")
        self.textEdit = QtWidgets.QTextEdit(Dialog)
        self.textEdit.setGeometry(QtCore.QRect(510, 280, 230, 160))
        self.textEdit.setObjectName("textEdit")
        self.textEdit.setEnabled(False)
        self.btn_3 = QtWidgets.QPushButton(Dialog)
        self.btn_3.setGeometry(QtCore.QRect(510, 490, 230, 30))
        self.btn_3.setObjectName("btn_3")
        self.img = QtWidgets.QLabel(Dialog)
        self.img.setGeometry(QtCore.QRect(510, 40, 224, 224))
        self.img.setText("")
        self.img.setObjectName("img")
        self.cam = QtWidgets.QLabel(Dialog)
        self.cam.setGeometry(QtCore.QRect(10, 40, 480, 480))
        self.cam.setText("")
        self.cam.setObjectName("cam")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.btn_1.setText(_translate("Dialog", "Start"))
        self.btn_2.setText(_translate("Dialog", "Stop"))
        self.btn_3.setText(_translate("Dialog", "Exit"))

#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, Ui_Dialog, NetFunc) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.initUI()
        self.server_ip = '192.168.101.102'
        self.server_port = 9000
        self.M2Cque = Queue() # MachineProcess to CameraProcess Queue
        self.C2Mque = Queue() # CameraProcess to MachineProcess Queue
        self.item_list = Queue()
        self.start = 0

        # Process.__init__(self, name='CameraProcess')
        NetFunc.__init__( self, self.server_ip, self.server_port)
        print( '[CameraProcess __init__]' )

        #메뉴툴바
        # self.mainMenu = self.menuBar()      # Menu bar
        # exitAction = QAction('&Exit', self)
        # exitAction.setShortcut('Ctrl+Q')
        # exitAction.triggered.connect(self.close)
        # self.fileMenu = self.mainMenu.addMenu('&File')
        # self.fileMenu.addAction(exitAction)
        
        #버튼에 기능을 연결하는 코드
        self.btn_1.clicked.connect(self.button1Function)
        self.btn_2.clicked.connect(self.button2Function)
        self.btn_3.clicked.connect(self.button3Function)
        
    def __del__( self ):
        print( '[WindowClass __del__]' )
        os._exit(0)
        
    def initUI(self):
        self.setWindowTitle('ARAF')
        self.setWindowIcon(QIcon('raspi.png'))
        self.show()

    #btn_1이 눌리면 작동할 함수
    def button1Function(self) :
        ps = Process(target=self.run())
        
        # ps.start()

    #btn_2가 눌리면 작동할 함수
    def button2Function(self) :
        self.start = 1
        
        #btn_3가 눌리면 작동할 함수
    def button3Function(self) :
        print("exit")
        os._exit(0)
        


    def sendImg2Server( self, img_roi): #, model):
        # set imencode parameter. set image quality 0~100 (100 is the best quality). default is 95
        encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),100]

        # image encoding,  encode_param is composed of [1, 100]
        result, imgencode = cv2.imencode('.jpg', img_roi, encode_param)
        if result==False:
            print("Error : result={}".format(result))

        # Show image
        # cv2.imshow('image', img_roi)
        
        # Convert numpy array
        roi_data = np.array(imgencode)

        # Convert String for sending Data
        stringData = roi_data.tostring()

        # Send to server
        self.sendData(stringData)
        print('go')
        # self.predictType(model, stringData)
        

    # def predictType( self, model, stringData ):
    #     imgdata = np.frombuffer(stringData, dtype='uint8')

    #     # img decode
    #     decimg=cv2.imdecode(imgdata,1)
    #     img_location = './img_file/buf.png'

    #     cv2.imwrite(img_location, decimg)

    #     """
    #     Create an array of the shape to supply to the Keras model
    #     The number of 'lengths' or images that can be placed in an array...
    #     ..determined by the first position of the tuple, in this case '1'
    #     """
    #     data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    #     image = Image.open(img_location)
    #     size = (224, 224)
    #     image = ImageOps.fit(image, size, Image.ANTIALIAS)


    #     #turn the image into a numpy array
    #     image_array = np.asarray(image)

    #     # Normalize the image
    #     normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

    #     # Load the image into the array
    #     data[0] = normalized_image_array

    #     prediction = model.predict(data)

    #     class_1 = prediction[0][0]
    #     class_2 = prediction[0][1]
    #     class_3 = prediction[0][2]
    #     class_4 = prediction[0][3]
    #     predict_class = max(prediction[0])

    #     if predict_class < 0.8:
    #         print("[ Cannot Distinguish ]")
    #         predict_type = 'ERR_001'
    #         classification = 'E'
    #     else:
    #         if class_1 == predict_class:
    #             print('prediction result : Dinosaur')
    #             predict_type = 'DSR_001'
    #             classification = 'A'

    #         elif class_2 == predict_class:
    #             print('prediction result : Airplane')
    #             predict_type = 'APL_001'
    #             classification = 'C'

    #         elif class_3 == predict_class:
    #             print('prediction result : Whale')
    #             predict_type = 'WAL_001'
    #             classification = 'B'

    #         elif class_4 == predict_class:
    #             print('prediction result : Empty')
    #             predict_type = 'ERR_001'
    #             classification = 'E'

    #         self.C2Mque.put(classification)

    #     cal = 'ADD'
    #     now = datetime.datetime.now()
    #     capdate = now.strftime( '%Y-%m-%d' )
    #     captime = now.strftime( '%H:%M:%S' )

    #     product_info = predict_type + cal + capdate + captime
    #     product_data = product_info.encode()


    #     self.sendData(product_data)


    def run(self):
        print('run1 start')
        conveyor_main = Conveyor_main()
        conveyor1 = Conveyor1()
        conveyor2 = Conveyor2()
        push1 = PushMotor1()
        push2 = PushMotor2()
        IR1 = IRSensor1(self.M2Cque, self.C2Mque)
        IR2 = IRSensor2(self.C2Mque, self.item_list)
        IR3 = IRSensor3(self.C2Mque, self.item_list)

        # thread start
        conveyor_main.start()
        conveyor1.start()
        conveyor2.start()
        # push1.start()
        # push2.start()
        IR1.start()
        # IR2.start()
        # IR3.start() 
        np.set_printoptions(suppress=True)

        cap = cv2.VideoCapture(-1)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,480)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)

        # load model.
        # model = load_model('initial_model.hdf5')
        try:
            while True:
                ret, img_color = cap.read()
                if ret == False:
                    continue
                img = cv2.cvtColor(img_color, cv2.COLOR_BGR2RGB) 
                h,w,c = img.shape
                qImg = QtGui.QImage(img.data, w, h, w*c, QtGui.QImage.Format_RGB888)
                pixmap = QtGui.QPixmap.fromImage(qImg)
                self.cam.setPixmap(pixmap)
                cv2.waitKey(1)
                QApplication.processEvents()

                if self.start == 1:
           
                    img_roi = cv2.resize(img_color, dsize=(224, 224))
                    img = cv2.cvtColor(img_roi, cv2.COLOR_BGR2RGB) 
                    h,w,c = img.shape
                    qImg = QtGui.QImage(img.data, w, h, w*c, QtGui.QImage.Format_RGB888)
                    pixmap = QtGui.QPixmap.fromImage(qImg)
                    self.img.setPixmap(pixmap)
                    item_name = '1'
                    now = datetime.datetime.now()
                    Capturedate = now.strftime( '%Y-%m-%d' )
                    Capturetime = now.strftime( '%H:%M:%S' )
                    path = r"./img/"
                    img_name = item_name + '_' + Capturedate+"_"+Capturetime+'.jpg'
                    f_dir = "./img/"
                    if os.path.isdir(f_dir):
                        pass
                    else:
                        os.makedirs(f_dir)
                    self.textEdit.append(f_dir+'  Create Folder')
                    save = cv2.imwrite(os.path.join(path, img_name),img_roi)
                    self.textEdit.append(img_name)
                    self.textEdit.append(str(save))
                    self.start = 0
                    self.sendImg2Server(img_roi)
            
            cap.release()
            cv2.destroyAllWindows()

        except KeyboardInterrupt :
            cv2.destroyAllWindows()
        finally:
            os._exit(0)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    myWindow = WindowClass() 
    myWindow.show()
    app.exec_()
