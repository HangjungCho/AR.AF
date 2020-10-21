from threading import Thread
from GPIO_ClassLib import RelayModule

class con1(Thread):
    def __init__(self):
        Thread.__init__(self, name='InfraerdSensorThread1')
        self.ports = (7)
        self.direction = ('con1')
        self.sensor = RelayModule( self.ports, self.direction )

    def __del__( self ):
        print( "Closing InfraerdSensorThread1" )

    def run(self):
        