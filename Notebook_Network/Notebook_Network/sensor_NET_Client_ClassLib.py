# sensor_NET_Client_ClassLib.py
from multiprocessing import Process, Queue
# from sensor_NET_ClassLib import USonicProcess, TempHumiProcess, LightProcess
import sensor_NET_ClassLib
import sys

class SensorClientProcess( Process ):
    def __init__( self, hostIP, hostPort ):
        Process.__init__( self, name = "SensorProcess" )
        self.host = hostIP
        self.port = hostPort

        print( '[SensorProcess __init__]' )

    def __del__( self ):
        #self.usonic.terminate()
        #self.tempHumi.terminate()
        #self.light.terminate()
        print( '[SensorProcess __del__]' )

    def run( self ):
        #self.usonic = USonicProcess( self.host, self.port )
        #self.usonic.start()

        #self.tempHumi = TempHumiProcess( self.host, self.port )
        #self.tempHumi.start()

        #self.light = LightProcess( self.host, self.port )
        #self.light.start()
        pass

if __name__ == '__main__':
    server_ip = input( "Input Server IP address : " )
    server_port = int( input( "Input Server Port number : " ) )
    sensorClientProcess = SensorClientProcess( server_ip, server_port )
    sensorClientProcess.start()
