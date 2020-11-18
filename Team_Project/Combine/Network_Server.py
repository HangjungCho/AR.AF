 # sensor_NET_Server_ClassLib.py
from multiprocessing import Process, Queue
from PIL import Image, ImageOps

import cv2
import numpy as np
import time, datetime
import socket
import sqlite3
import sys
import os

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
                clientImgProcess.start()

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

    def saveTrainingImage(self, imgdata, dataset):
        # save image
        dir_flag = 1
        capdate = dataset[28:38]
        captime = dataset[38:53]
        generator_type = dataset[53:58]
        class_name = dataset[58:]
        print('capdate : {}'.format(capdate))
        print('captime : {}'.format(captime))
        print('generator_type : {}'.format(generator_type))
        print('class_name : {}'.format(class_name))
        date = capdate.replace('-', '') + '_' + captime.replace(':', '')
        img_name = date +'.jpg'

        path, dirs, files = next(os.walk("./dataset/"+generator_type))
        classification_num = len(dirs)

        for dir in dirs:
            if dir[3:] == class_name:
                dir_flag = 0
                dir_buf = dir

        print('dir_flag = {}'.format(dir_flag))
        if dir_flag:
            directory_path = './dataset/'+generator_type+'/'+str(classification_num)+'. '+class_name
            if not os.path.exists(directory_path):
                os.mkdir(directory_path)
        
        else:
            directory_path = './dataset/'+generator_type+'/'+ dir_buf
            
        img_location = directory_path+'/'+img_name
        print('img_location : {}'.format(img_location))
        cv2.imwrite(img_location, imgdata)
        
    
    def insertDB( self, imgdata, product):
        conn = sqlite3.connect( 'araf.db' )
        product_type = product[:7]
        print(product_type)

        with conn:
            cursor = conn.cursor()
            cursor.execute( 'SELECT num FROM Count WHERE p_type = ?', (product_type,))
            count = cursor.fetchall()


        # depart information
        cal = product[7:10]
        realdate = product[10:20]
        realtime = product[20:]


        # save image
        now_date = realdate.replace('-', '') + '_' + realtime.replace(':', '')
        img_name = product_type + '_' + now_date+'.png'
        img_location = './static/img_file/'+img_name
        db_img = './img_file/'+img_name
        cv2.imwrite(img_location, imgdata)
        web_img_name = 'img/product/' + product_type + '.png'


        # ADD count
        if count == []:
            # 없던 항목이었다면 Count 와 ErrStat table의 레코드에 추가해주자
            print('ADD new Category')
            with conn:
                cursor = conn.cursor()
                cursor.execute( 'INSERT INTO Count(p_type, num, img) VALUES(?, ?, ?)', (product_type, 0, web_img_name) )
                cursor.execute( 'INSERT INTO ErrStat(p_type, num) VALUES(?, ?)', (product_type, 0) )
                conn.commit()


        cursor.execute( 'SELECT num FROM ErrStat WHERE p_type = ?', (product_type,))
        err_cnt = cursor.fetchall()
        
        error = 0 # 임시로 error을 0으로 두었으나 이건 Machine_Control에서 판명해서 데이터전송을 통해 전달해줘야 하는 정보임.
        # 그러나 제품이 에러가난 경우를 판별하는 기준이 갖추어 있지 않으므로 여기서 임의로 에러가 없다는 0값을 집어넣어준것 뿐임
        
        data = product_type, cal, count, error, realdate, realtime, db_img
        

        with conn:
            cursor = conn.cursor()
            # 에러가 발생할 경우 Count 테이블은 카운트하지 않고 Quantity 테이블의 count항목도 증가하면 안된다.
            if error == 1:
                cursor.execute( 'UPDATE ErrStat SET num = ? WHERE p_type = ?', (err_cnt[0][0]+1, product_type))
                cursor.execute( 'INSERT INTO Quantity(p_type, cal, count, error, date, time, img) VALUES(?, ?, ?, ?, ?, ?, ?)', product_type, cal, count, error, realdate, realtime, db_img )
            
            elif error == 0:
                data = product_type, cal, (count[0][0]+1), error, realdate, realtime, db_img
                print('data : {}'.format(data))
                # 에러가 발생할 경우 Count 테이블과 Quantity 테이블의 수량 항목이 증가해야 한다.
                cursor.execute( 'UPDATE  Count SET num = ? WHERE p_type = ? ', (count[0][0]+1, product_type) )
                cursor.execute( 'INSERT INTO Quantity(p_type, cal, count, error, date, time, img) VALUES(?, ?, ?, ?, ?, ?, ?)', data )

            
            conn.commit()

    def run( self ):
        # try:
            
        while True:
            
            getlength = self.client_sock.recv( 28 )
            if int(getlength) > 4000:
                print('get 1')
                """ image data protocol """
                getdata1 = self.recvall(self.client_sock, int(getlength))
                imgdata = np.frombuffer(getdata1, dtype='uint8') 

                # img decode
                decimg=cv2.imdecode(imgdata,1)
            else:
                if int(getlength) == 28:
                    print('get 2')
                    """ product information protocol """ 
                    getdata2 = self.recvall(self.client_sock, int(getlength))
                    # insert all data in Database
                    product = getdata2.decode()
                    self.insertDB(decimg, product)
                
                else:
                    print('get 3')
                    getdata2 = self.recvall(self.client_sock, int(getlength))
                    # insert all data in Database
                    dataset = getdata2.decode()
                    self.saveTrainingImage(decimg, dataset)



        # except FileNotFoundError:
        #     pass

        # except KeyboardInterrupt:
        #     pass
        # finally:
        #     print( "[ Disconnection client ]")
        #     sys.exit()

if __name__ == '__main__':
    server_ip = '192.168.0.125'
    server_port = 9000
    serverManageProcess = ReceptionProcess( server_ip, server_port )
    serverManageProcess.start()