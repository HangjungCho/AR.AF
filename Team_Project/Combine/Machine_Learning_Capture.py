from PyQt5 import QtCore, QtGui, QtWidgets, uic
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QFont

# from PyQt5.QtGui import QPainter, QPen, QColor, QBrush, QFont
import cv2
import threading
import datetime
import os
import socket
import numpy as np


# global variation
running = False
start = 0
count = 0
generator_type = 'train'

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


class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(750, 540)


        # ---------- Label UX Design --------- #
        self.Add_class = QtWidgets.QTextEdit(Dialog)
        self.Add_class.setGeometry(QtCore.QRect(600, 370, 140, 30))
        self.Add_class.setObjectName("Add_class")    
        # ------------------------------------- #

        # ---------- Button Design ------------ #
        self.btn_1 = QtWidgets.QPushButton(Dialog)
        self.btn_1.setGeometry(QtCore.QRect(510, 450, 105, 30))
        self.btn_1.setObjectName("btn_1")

        self.btn_2 = QtWidgets.QPushButton(Dialog)
        self.btn_2.setGeometry(QtCore.QRect(510, 490, 105, 30))
        self.btn_2.setObjectName("btn_2")
        
        self.btn_3 = QtWidgets.QPushButton(Dialog)
        self.btn_3.setGeometry(QtCore.QRect(635, 450, 105, 70))
        self.btn_3.setObjectName("btn_3")
        # ----------------------------------------

        # --------- Radio button Design ---------- #
        self.groupBox_rad1 = QtWidgets.QRadioButton('Train', self)
        self.groupBox_rad1.setGeometry(QtCore.QRect(530, 410, 80, 30))
        self.groupBox_rad1.setObjectName("radio_1")
        self.groupBox_rad1.setChecked(True)
        
        self.groupBox_rad2 = QtWidgets.QRadioButton('Tests', self)
        self.groupBox_rad2.setGeometry(QtCore.QRect(635, 410, 80, 30))
        self.groupBox_rad2.setObjectName("radio_2")
        # ----------------------------------------- #

        self.textEdit = QtWidgets.QTextEdit(Dialog)
        self.textEdit.setGeometry(QtCore.QRect(510, 270, 225, 95))
        self.textEdit.setObjectName("textEdit")
        self.textEdit.setEnabled(False)





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
        self.btn_2.setText(_translate("Dialog", "Exit"))
        self.btn_3.setText(_translate("Dialog", "Capture"))

    # --------------- Text ------------- #    
    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.draw_text(qp)
        qp.end()
    
    def draw_text(self, qp):
        qp.setFont(QFont('Consolas', 9))
        qp.drawText(510, 390, 'Class Name:')
    # ---------------------------------- #

# Define WindowClass to display Window
class WindowClass(QMainWindow, Ui_Dialog, NetFunc) :
    def __init__(self, host, port) :
        # super().__init__()
        QMainWindow.__init__( self )
        Ui_Dialog.__init__( self )
        NetFunc.__init__( self, host, port )
        self.setupUi(self)
        self.initUI()

        
        # Menu Tool Bar
        # self.mainMenu = self.menuBar()      # Menu bar
        # exitAction = QAction('&Exit', self)
        # exitAction.setShortcut('Ctrl+Q')
        # exitAction.triggered.connect(self.close)
        # self.fileMenu = self.mainMenu.addMenu('&File')
        # self.fileMenu.addAction(exitAction)

        # Input Text Window
        # self.lineedit_Test.textChanged.connect(self.lineeditTextFunction)
        # self.lineedit_Test.returnPressed.connect(self.printTextFunction)
        # self.btn_changeText.clicked.connect(self.changeTextFunction)

        # Connet Button with Function
        self.btn_1.clicked.connect(self.button1Function) # start
        self.btn_2.clicked.connect(self.button2Function) # exit
        self.btn_3.clicked.connect(self.button3Function) # capture

        self.groupBox_rad1.clicked.connect(self.groupboxRadFunction)
        self.groupBox_rad2.clicked.connect(self.groupboxRadFunction)
        
    def __del__( self ):
        print( '[WindowClass __del__]' )
        global running
        running = False
        sys.exit(app.exec_())

    def sendImg2Server( self, img_roi, generator_type ):
        # set imencode parameter. set image quality 0~100 (100 is the best quality). default is 95
        encode_param=[int(cv2.IMWRITE_JPEG_QUALITY),100]

        # image encoding,  encode_param is composed of [1, 100]
        result, imgencode = cv2.imencode('.jpg', img_roi, encode_param)
        if result==False:
            print("Error : result={}".format(result))
        
        
        # Convert numpy array
        roi_data = np.array(imgencode)

        # Convert String for sending Data
        bytesData = roi_data.tobytes()

        # Send to server
        self.sendData(bytesData)
        now = datetime.datetime.now()
        Capturedate = now.strftime( '%Y-%m-%d' ) # 10
        Capturetime = now.strftime( '%H:%M:%S:%f' ) # 15

        self.textEdit.append('\nDate : {}'.format(Capturedate))
        self.textEdit.append('Time : {}'.format(Capturetime))
        self.textEdit.append('Generator Type : {}'.format(generator_type))
        self.textEdit.append('Class Name : {}'.format(self.getclassname))
        self.textEdit.append('Image Capture Complete')
    
        dummy = ''
        for i in range(28):
            dummy = dummy + 'a'

        data = dummy + Capturedate + Capturetime + generator_type + self.getclassname
        print(len(dummy))
        print(len(data))
        encode_data = data.encode()
        self.sendData(encode_data)

        
    def run(self):
        global running
        global start
        global count
        global generator_type
        cap = cv2.VideoCapture(-1)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH,480)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT,480)
        while running:
            ret,img_color = cap.read()
            if ret:
                img = cv2.cvtColor(img_color, cv2.COLOR_BGR2RGB) 
                h,w,c = img.shape
                qImg = QtGui.QImage(img.data, w, h, w*c, QtGui.QImage.Format_RGB888)
                pixmap = QtGui.QPixmap.fromImage(qImg)
                self.cam.setPixmap(pixmap)
                cv2.waitKey(0)
                QApplication.processEvents()
            else:
                break

            if start == 1:
                img_roi = cv2.resize(img_color, dsize=(224, 224))

                img = cv2.cvtColor(img_roi, cv2.COLOR_BGR2RGB) 
                h,w,c = img.shape
                qImg = QtGui.QImage(img.data, w, h, w*c, QtGui.QImage.Format_RGB888)
                pixmap = QtGui.QPixmap.fromImage(qImg)
                self.img.setPixmap(pixmap)

            

                ''' ### send image data to server ### '''
                self.sendImg2Server(img_roi, generator_type)

                count += 1
                start = 0
        cap.release()
        cv2.destroyAllWindows()
    
    
    def initUI(self):
        self.setWindowTitle('ARAF')
        self.setWindowIcon(QIcon('raspi.png'))
        self.show()
        
    def on_click(self):
        self.lbl.setText(self.qle.text())
        self.lbl.adjustSize()



    #btn_1 Function
    def button1Function(self) :
        self.btn_1.setEnabled(False)
        self.btn_2.setEnabled(True)
        self.btn_3.setEnabled(True)
        global running
        running = True
        th = threading.Thread(target=self.run())
        th.start()

    # btn_2 Function
    def button2Function(self) :
        print("exit")
        global running
        running = False
        sys.exit( app.exec_() )

    def button3Function(self) :
        global start
        self.getclassname = self.Add_class.toPlainText()
        start = 1

    def groupboxRadFunction(self) :
        global generator_type
        if self.groupBox_rad1.isChecked():
            generator_type = 'train'
        elif self.groupBox_rad2.isChecked():
            generator_type = 'tests'

if __name__ == "__main__" :
    server_ip = '192.168.0.125'
    server_port = 9000
    app = QApplication(sys.argv)
    myWindow = WindowClass(server_ip, server_port) 
    myWindow.show()
    app.exec_()