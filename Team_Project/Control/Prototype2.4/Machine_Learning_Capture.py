# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ARAF3.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets, uic
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon
import cv2
import threading
import datetime
import os

running = False
start = 0
count = 0

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
        self.btn_2.setText(_translate("Dialog", "Capture"))
        self.btn_3.setText(_translate("Dialog", "Exit"))

#화면을 띄우는데 사용되는 Class 선언
class WindowClass(QMainWindow, Ui_Dialog) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.initUI()
        
        #메뉴툴바
        self.mainMenu = self.menuBar()      # Menu bar
        exitAction = QAction('&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.triggered.connect(self.close)
        self.fileMenu = self.mainMenu.addMenu('&File')
        self.fileMenu.addAction(exitAction)
        
        #버튼에 기능을 연결하는 코드
        self.btn_1.clicked.connect(self.button1Function)
        self.btn_2.clicked.connect(self.button2Function)
        self.btn_3.clicked.connect(self.button3Function)
        
    def __del__( self ):
        print( '[WindowClass __del__]' )
        global running
        running = False
        sys.exit(app.exec_())
        
    def run(self):
        global running
        global start
        global count
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

                now = datetime.datetime.now()
                Capturedate = now.strftime( '%Y-%m-%d' )
                Capturetime = now.strftime( '%H:%M:%S' )
                path = r"./img/"
                img_name = str(count) + '_' + Capturedate+"_"+Capturetime+'.jpg'
                f_dir = "./img/"
                if  os.path.isdir(f_dir):
                    pass
                else:
                    os.makedirs(f_dir)
                    self.textEdit.append(f_dir+'  Create Folder')
                save = cv2.imwrite(os.path.join(path, img_name),img_roi)
                self.textEdit.append(img_name)
                self.textEdit.append(str(save))
                count += 1
                start = 0
        cap.release()
        cv2.destroyAllWindows()
    
    
    def initUI(self):
        self.setWindowTitle('ARAF')
        self.setWindowIcon(QIcon('raspi.png'))
        self.show()

    #btn_1이 눌리면 작동할 함수
    def button1Function(self) :
        global running
        running = True
        th = threading.Thread(target=self.run())
        th.start()

    #btn_2가 눌리면 작동할 함수
    def button2Function(self) :
        global start
        start = 1
        
        #btn_3가 눌리면 작동할 함수
    def button3Function(self) :
        print("exit")
        global running
        running = False
        sys.exit(app.exec_())

if __name__ == "__main__" :
    app = QApplication(sys.argv)
    myWindow = WindowClass() 
    myWindow.show()
    app.exec_()