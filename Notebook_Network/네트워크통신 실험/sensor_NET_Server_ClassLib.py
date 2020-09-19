# sensor_NET_Server_ClassLib.py
from multiprocessing import Process, Queue

import time
import socket
#import sqlite3
import sys

class SensorReceptionProcess( Process ):
    def __init__( self, ip, port ):
        Process.__init__( self, name = "SensorReceptionProcess" )

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

        self.DATE_BUFSIZE = 10
        self.TIME_BUFSIZE = 8
        self.KIND_BUFSIZE = 5
        self.VALUE_BUFSIZE = 11

        self.client_sock = c_sock
        self.client_address = c_address
        print( '[ClientProcess __init__]' )

    def __del__( self ):
        print( '[ClientProcess __del__]' )
        self.client_sock.close()



    def run( self ):
        loop = True

        try:
            while ( loop ):
                print( "receiving waiting...\n" )
                recv_kind = self.client_sock.recv( self.KIND_BUFSIZE )
                if ( recv_kind != 'END'):
                    recv_date = self.client_sock.recv( self.DATE_BUFSIZE )
                    recv_time = self.client_sock.recv( self.TIME_BUFSIZE )
                    recv_value = self.client_sock.recv( self.VALUE_BUFSIZE )
                    print( "receiving complete..." )

                    date_data = recv_date.decode()
                    time_data = recv_time.decode()
                    kind_data = recv_kind.decode()
                    value_data = float( recv_value.decode() )

                    if ( len( kind_data ) >= self.KIND_BUFSIZE and
                        len( date_data ) >= self.DATE_BUFSIZE and
                        len( time_data ) >= self.TIME_BUFSIZE ):
                        data = date_data, time_data, kind_data, value_data

                        #conn = sqlite3.connect( 'sensor.db' )
                        #with conn:
                        #    cursor = conn.cursor()
                        #    cursor.execute( 'INSERT INTO sensor_measure( date, time, kind, measurevalue ) VALUES ( ?, ?, ?, ? )', data )
                        #    conn.commit()
                        print( "{0} {1} {2} {3}\ninsert complete...\n".format( kind_data, date_data, time_data, value_data ) )
                else:
                    loop = False

        except FileNotFoundError:
            pass

        except KeyboardInterrupt:
            pass

        finally:
            print( "[ Disconnection client ]")
            sys.exit()

def main():
    sensorManageProcess = SensorReceptionProcess( '192.168.43.143', 9000 )
    sensorManageProcess.start()
    sensorManageProcess.join()
    print( "Stop Main Process..." )

if __name__ == '__main__':
    main()
