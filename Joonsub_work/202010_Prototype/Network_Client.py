# Network_Client.py
from multiprocessing import Process, Queue
import socket
import sys
import time, datetime
from Machine_Control import MachineProcess

class NetClient(Process):
    def __init__( self, hostIP, hostPort ):
        Process.__init__(self, name='NetClient')
        self.host = hostIP
        self.port = hostPort

        self.sock = socket.socket( socket.AF_INET, socket.SOCK_STREAM )
        self.server_address = ( self.host, self.port )
        self.sock.connect( self.server_address )

    def __del__( self ):
        self.sock.close()
        print( "Closing connection to the server" )
        sys.exit()

    def run( self ):
        self.MP = MachineProcess(self.host, self.port)
        self.MP.start()
        
if __name__ == '__main__':
    server_ip = '192.168.0.84'
    server_port = 9000
    sensorClientProcess = MachineProcess( server_ip, server_port )
    sensorClientProcess.start()