# sensor_NET_ClassLib.py
# 각 센서별로 주기를 다르게 받아오기 때문에 나눠준다 Process를 나눴지만 Thread로 나눠도 상관없음
from multiprocessing import Process, Queue

import sqlite3
import socket
import time, datetime

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
