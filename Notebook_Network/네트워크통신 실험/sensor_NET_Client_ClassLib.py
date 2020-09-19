# sensor_NET_Client_ClassLib.py
from multiprocessing import Process, Queue

import sqlite3
import socket
import time, datetime
import sys

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

class SensorClientProcess( Process, NetClient ):
    def __init__( self, hostIP, hostPort ):
        Process.__init__( self, name = "SensorProcess" )
        NetClient.__init__( self, hostIP, hostPort )
        
        self.value = 30
        self.host = hostIP
        self.port = hostPort

        print( '[Network]Process __init__]' )

    def __del__( self ):
        print( '[NetworkProcess __del__]' )

    def run( self ):
        try:
            loop = True
            print( "Data Send looping....." )
            while loop:
                now = datetime.datetime.now()
                measuredate = now.strftime( '%Y-%m-%d' )
                measuretime = now.strftime( '%H:%M:%S' )
                # distance = str( '{0:5.2f}'.format( self.usonic.USONIC_getDistance() ) )
                distance = '30cm'
                print( '\n[sleep : {0}]\n[{1}]\n[{2}]\n[{3}]\n[{4}]\n'.format( self.value, 'MEASU', measuredate, measuretime, distance ) )

                self.sendData( 'type A' )
                self.sendData( measuredate )
                self.sendData( measuretime )
                self.sendData( distance )
                time.sleep( self.value )

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
