# Network_Client.py
from multiprocessing import Process, Queue
import socket
import sys
import time, datetime
from Machine_Control import MachineProcess#, MainMotor1, MainMotor2, DischargeMotor1, DischargeMotor2, InfraerdSensorThread1, InfraerdSensorThread2, RelayModuleThread1, RelayModuleThread2 

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

    def run( self ):
        self.MP = MachineProcess(self.host, self.port)
        # self.MM1 = MainMotor1()
        # self.MM2 = MainMotor2()
        # self.DM1 = DischargeMotor1()
        # self.DM2 - DischargeMotor2
        # self.IS1 = InfraerdSensorThread1()
        # self.IS2 = InfraerdSensorThread2()
        # self.RM1 = RelayModuleThread1()
        # self.RM2 = RelayModuleThread2()
        self.MP.start()
        # self.MM1.start()
        # self.MM2.start()
        # self.DM1.start()
        # self.DM2.start()
        # self.IS1.start()
        # self.IS2.start()
        # self.RM1.start()
        # self.RM2.start()
        
if __name__ == '__main__':
    server_ip = '1.240.109.246'
    server_port = 9000
    sensorClientProcess = MachineProcess( server_ip, server_port )
    sensorClientProcess.start()