# sensor_NET_Server_ClassLib.py
from multiprocessing import Process, Queue

import time
import socket
import sqlite3
import sys

class ReceptionProcess( Process ):
    def __init__( self, ip, port ):
        Process.__init__( self, name = "ReceptionProcess" )

        self.server_ip = ip
        self.server_port = port
        self.backlog = 5 # 큐가 보유 할 보류중인 연결 수를 지정 최소값 : 0, 보통 5로 지정 연결수를 넘어가면 삭제된다!

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

                clientProcess = ClientProcess( client_sock, address )
                clientProcess.start()

            except Exception as e:
                print( e )

            except KeyboardInterrupt as e:
                print( e )
                sys.exit()

class ClientProcess( Process ):
    def __init__( self, c_sock, c_address ):
        Process.__init__( self, name = "ClientProcess" )
        self.KIND_BUFSIZE = 25

        self.client_sock = c_sock
        self.client_address = c_address
        print( '[ClientProcess __init__]' )

    def __del__( self ):
        print( '[ClientProcess __del__]' )
        self.client_sock.close()

    def Insert_db( self, product):
        # 테스트용 코드
        # -------------
        conn = sqlite3.connect( 'araf.db' )
        product_type = product[0]

        with conn:
            cursor = conn.cursor()
            cursor.execute( 'SELECT num FROM Count WHERE type = ?', (product_type, ))
            count = cursor.fetchall()

        cal = product[1:4]
        count = count[0][0] + 1
        realdate = product[4:14]
        realtime = product[14:]
        data = product_type, cal,count,realdate, realtime
        conn = sqlite3.connect( 'araf.db' )

        with conn:
            cursor = conn.cursor()
            cursor.execute( 'INSERT INTO Quantity(type, cal, count, date, time) VALUES(?, ?, ?, ?, ?)', data )
            cursor.execute( 'UPDATE  Count SET num = ? WHERE type = ? ', (count, product_type) )
            conn.commit()

    def run( self ):
        try:
            loop = True
            while ( loop ):
                print( "receiving waiting...\n" )
                recv_kind = self.client_sock.recv( self.KIND_BUFSIZE )
                print("recv : {}".format(recv_kind))
                if ( recv_kind != b'END'):
                    item_data = recv_kind.decode()
                    self.Insert_db(item_data)
                    print('item_data : {}'.format(item_data))
                    print( "receiving complete..." )
                else:
                    loop = False
                    sys.exit()

        except FileNotFoundError:
            pass

        except KeyboardInterrupt:
            pass

        finally:
            print( "[ Disconnection client ]")
            sys.exit()


if __name__ == '__main__':
    server_ip = '1.240.109.246'
    server_port = 9000
    serverManageProcess = ReceptionProcess( server_ip, server_port )
    serverManageProcess.start()