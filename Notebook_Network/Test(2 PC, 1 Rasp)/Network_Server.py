# sensor_NET_Server_ClassLib.py
from multiprocessing import Process, Queue
from ControlSection import USonicThread, DCMotorThread

import time
import socket
#import sqlite3
import sys
insert_flag = 0
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
        global insert_flag
        while True:
            try:
                client_sock, address = self.server_sock.accept()
                print( '[ Connection client IP : {0} ]'.format( address ) )
                print( 'Client connect Waiting.....\n' )

                clientProcess = ClientProcess( client_sock, address )
                clientProcess.start()
                usonic = USonicThread(insert_flag)
                usonic.start()
                dcmotor = DCMotorThread(insert_flag)
                dcmotor.start()

            except Exception as e:
                print( e )

            except KeyboardInterrupt as e:
                print( e )
                sys.exit()

class ClientProcess( Process ):
    def __init__( self, c_sock, c_address ):
        Process.__init__( self, name = "ClientProcess" )
        self.KIND_BUFSIZE = 2

        self.client_sock = c_sock
        self.client_address = c_address
        print( '[ClientProcess __init__]' )

    def __del__( self ):
        print( '[ClientProcess __del__]' )
        self.client_sock.close()


    def run( self ):
        try:
            global insert_flag
            loop = True
            while ( loop ):
                print( "receiving waiting...\n" )
                recv_kind = self.client_sock.recv( self.KIND_BUFSIZE )
                print("recv : {}".format(recv_kind))
                if ( recv_kind != b'END'):
                    kind_data = recv_kind.decode()
                    print('kind : {}'.format(kind_data))
                    print( "receiving complete..." )
                    insert_flag = 1
                    
                    time.sleep(1)
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
    server_ip = '192.168.0.10'
    server_port = 9000
    sensorManageProcess = ReceptionProcess( server_ip, server_port )
    sensorManageProcess.start()