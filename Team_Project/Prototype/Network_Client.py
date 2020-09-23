# Network_Client.py
from Machine_Vision import MachineVisionProcess
from multiprocessing import Process, Queue
import sys

#import sqlite3
#import socket
#import time, datetime
#import math

class MvisionNetProcess( Process ):
    def __init__( self, hostIP, hostPort ):
        Process.__init__( self, name = "SensorProcess" )
        self.host = hostIP
        self.port = hostPort
        print( '[Network]Process __init__]' )

    def __del__( self ):
        print( '[NetworkProcess __del__]' )

    def run( self ):
        self.Mvision = MachineVisionProcess(self.host, self.port)  
        self.Mvision.start()

        
if __name__ == '__main__':
    server_ip = '192.168.0.2'
    server_port = 9000
    sensorClientProcess = MvisionNetProcess( server_ip, server_port )
    sensorClientProcess.start()