# Network_Client.py
from Machine_Vision import MachinVisionProcess
from multiprocessing import Process, Queue

import sqlite3
import socket
import time, datetime
import sys
import math

class SensorClientProcess( Process ):
    def __init__( self, hostIP, hostPort ):
        Process.__init__( self, name = "SensorProcess" )
        
        self.value = 1
        self.host = hostIP
        self.port = hostPort

        print( '[Network]Process __init__]' )

    def __del__( self ):
        print( '[NetworkProcess __del__]' )

    def run( self ):
        try:
            self.Mvision = MachinVisionProcess(self.host, self.port)
            self.Mvision.start()

        except ( RuntimeError ):
            print( "Runtime Error" )

        except KeyboardInterrupt:
            sys.exit()
        finally:
            self.sendData( 'END' )

if __name__ == '__main__':
    server_ip = input( "Input Server IP address : " )
    server_port = int( input( "Input Server Port number : " ) )
    sensorClientProcess = SensorClientProcess( server_ip, server_port )
    sensorClientProcess.start()
