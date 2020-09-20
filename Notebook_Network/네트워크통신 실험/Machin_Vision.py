import tensorflow as tf
import cv2
import numpy as np 
import math
from tensorflow.keras.models import load_model
from multiprocessing import Process, Queue

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

    def receiveData( self ):
        try:
            receiveData = self.sock.recv( 20 ).decode()
            print( "Receiving --> {0}\n".format( receiveData ) )

        except socket.errno as e:
            print( "Socket error: %s" %str(e) )
        except Exception as e:
            print( "Other exception: %s" %str(e) )
        return receiveData

class MachinVisionProcess( Process ):

    def __init__( self, ip, port ):
        Process.__init__( self, name = "MachinVisionProcess" )
        self.ip = ip
        self.port = port
        print( '[MachinVisionProcess __init__]' )

    def __del__( self ):
        print( '[MachinVisionProcess __del__]' )
        self.server_sock.close()

    def process(self, img_input):
        gray = cv2.cvtColor(img_input, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, (28, 28), interpolation=cv2.INTER_AREA)
        (thresh, img_binary) = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)
        h,w = img_binary.shape

        ratio = 100/h
        new_h = 100
        new_w = w * ratio

        img_empty = np.zeros((110,110), dtype=img_binary.dtype)
        img_binary = cv2.resize(img_binary, (int(new_w), int(new_h)), interpolation=cv2.INTER_AREA)
        img_empty[:img_binary.shape[0], :img_binary.shape[1]] = img_binary
        img_binary = img_empty

        cnts = cv2.findContours(img_binary.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 컨투어의 무게중심 좌표를 구합니다. 
        M = cv2.moments(cnts[0][0])
        print('{}, {}, {}'.format(M["m00"],M["m10"],M["m01"])) # Zero Division 에러 발생을 체크하기 위해 임시로 넣었습니다.
        center_x = (M["m10"] / M["m00"])
        center_y = (M["m01"] / M["m00"])

        # 무게 중심이 이미지 중심으로 오도록 이동시킵니다. 
        height,width = img_binary.shape[:2]
        shiftx = width/2-center_x
        shifty = height/2-center_y

        Translation_Matrix = np.float32([[1, 0, shiftx],[0, 1, shifty]])
        img_binary = cv2.warpAffine(img_binary, Translation_Matrix, (width,height))

        img_binary = cv2.resize(img_binary, (28, 28), interpolation=cv2.INTER_AREA)
        flatten = img_binary.flatten() / 255.0
        return flatten

    def run(self):
        cap = cv2.VideoCapture(1)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        model = load_model('04-0.0781.hdf5')  

        while 1:
            ret, img_color = cap.read()

            if ret == False:
                break;

            img_input = img_color.copy()
            cv2.rectangle(img_color, (250, 150),  (width-250, height-150), (0, 0, 255), 3)
            cv2.imshow('bgr', img_color)
            img_roi = img_input[150:height-150, 250:width-250]

            key = cv2.waitKey(1)
            try:
                if key == 27:
                    break
                elif key == 32:
                    flatten = process(img_roi)

                    predictions = model.predict(flatten[np.newaxis,:])

                    with tf.compat.v1.Session() as sess:
                        print(tf.argmax(predictions, 1).eval())
                    cv2.imshow('img_roi', img_roi)
            #         cv2.waitKey(0)
            except:
                continue

        cap.release()
        cv2.destroyAllWindows()




