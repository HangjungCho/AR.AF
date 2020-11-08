 # sensor_NET_Server_ClassLib.py
from multiprocessing import Process, Queue
from PIL import Image, ImageOps

import cv2
import numpy as np
import time, datetime
import socket
import sqlite3
import sys
import datetime

class ReceptionProcess( Process ):
    def __init__( self, ip, port ):
        Process.__init__( self, name = "ReceptionProcess" )

        self.server_ip = ip
        self.server_port = port
        self.backlog = 5 #

        self.server_sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.server_sock.setsockopt( socket.SOL_SOCKET, socket.SO_REUSEADDR, 1 )
        self.server_address = ( self.server_ip, self.server_port )
        self.server_sock.bind( self.server_address )
        print( "[ Server IP : {0:15s} - {1:5d} ]".format( self.server_ip, self.server_port ) )

        self.server_sock.listen( self.backlog )
        print( '[SensorReceptionProcess __init__]' )

    def __del__( self ):
        print( '[SensorReceptionProcess __del__]' )
        self.server_sock.close() 

    def run( self ):
        while True:
            try:
                client_sock, address = self.server_sock.accept()
                print( '[ Connection client IP : {0} ]'.format( address ) )
                print( 'Client connect Waiting.....\n' )

                clientImgProcess = ClientImgProcess( client_sock, address )
                # clientInfoProcess = ClientInfoProcess( client_sock, address )
                clientImgProcess.start()
                # clientInfoProcess.start()

            except Exception as e:
                print( e )

            except KeyboardInterrupt as e:
                print( e )
                sys.exit()

class ClientImgProcess( Process ):
    def __init__( self, c_sock, c_address ):
        Process.__init__( self, name = "ClientImgProcess" )
        # self.KIND_BUFSIZE = 28
        self.client_sock = c_sock
        self.client_address = c_address
        print( '[ClientProcess __init__]' )

    def __del__( self ):
        print( '[ClientProcess __del__]' )
        self.client_sock.close()

    def recvall( self, sock, count ):
        buf = b''
        while count:
            newbuf = sock.recv(count)
            if not newbuf: return None
            buf += newbuf
            count -= len(newbuf)
        return buf
    
    def insertDB( self, imgdata):#, product):
        # conn = sqlite3.connect( 'araf.db' )
        # product_type = product[:7]

        # with conn:
        #     cursor = conn.cursor()
        #     cursor.execute( 'SELECT num FROM Count WHERE p_type = ?', (product_type,))
        #     count = cursor.fetchall()


        # # depart information
        # cal = product[7:10]
        # realdate = product[10:20]
        # realtime = product[20:]


        # save image
        # now_date = realdate.replace('-', '') + '_' + realtime.replace(':', '')
        now_date = datetime.datetime.now()
        img_name = str(now_date)+'.png'
        img_location = r'./img_file/132.jpg'
        cv2.imwrite(img_location, imgdata)
        print('img_save')


        # # ADD count
        # if count == []:
        #     # 없던 항목이었다면 Count table의 column에 추가해주자
        #     with conn:
        #         cursor = conn.cursor()
        #         cursor.execute( 'INSERT INTO Count(p_type, num) VALUES(?, ?)', (product_type, 1) )
        #         conn.commit()
        #     count = 1
        # else:
        #     count = count[0][0] + 1

        # data = product_type, cal, count, realdate, realtime, img_location
        

        # with conn:
        #     cursor = conn.cursor()
        #     cursor.execute( 'INSERT INTO Quantity(p_type, cal, count, date, time, img) VALUES(?, ?, ?, ?, ?, ?)', data )
        #     cursor.execute( 'UPDATE  Count SET num = ? WHERE p_type = ? ', (count, product_type) )
        #     conn.commit()

    def run( self ):
        # try:
            
        while True:

            """ image data protocol """
            getlength1 = self.client_sock.recv( 28 )
            getdata1 = self.recvall(self.client_sock, int(getlength1))
            imgdata = np.frombuffer(getdata1, dtype='uint8') 
            #


            # img decode
            decimg=cv2.imdecode(imgdata,1)



            # """ product information protocol """ 
            # getlength2 = self.client_sock.recv( 28 )
            # getdata2 = self.recvall(self.client_sock, int(getlength2))
            # # insert all data in Database
            # product = getdata2.decode()
            print('get_img')
            self.insertDB(decimg)#, product)

        # except FileNotFoundError:
        #     pass

        # except KeyboardInterrupt:
        #     pass
        # finally:
        #     print( "[ Disconnection client ]")
        #     sys.exit()

if __name__ == '__main__':
    server_ip = '192.168.101.102'
    server_port = 9000
    serverManageProcess = ReceptionProcess( server_ip, server_port )
    serverManageProcess.start()