from threading import Thread
from GPIO_ClassLib import USONIC, DCMOTOR, JOGSW
import time
distance = 0 # global

class USonicThread(Thread):
    def __init__(self):
        Thread.__init__(self, name='UsonicThread')
        self.ports = (0,1)
        self.direction = ( 'out', 'in' )
        self.usonic = USONIC( self.ports, self.direction )

    def __del__( self ):
        print( "Closing UsosnicThread" )

    def run(self):
        while True:
            global distance
            self.usonic.USONIC_send()
            self.usonic.USONIC_receive()
            distance = self.usonic.USONIC_getDistance()
            distance = round(distance,2)
            print('Distance : {:.2f}cm'.format(distance))

class DCMotorThread(Thread):
    def __init__(self):
        Thread.__init__(self, name='DCMotorThread')
        self.ports = (4,25,12)
        self.direction = ( 'p', 'n', 'en' )
        self.dcmotor = DCMOTOR( self.ports, self.direction )

    def __del__( self ):
        print( "Closing DCMotorThread" )

    def run(self):
        while True:
            global distance

            if distance <= 9.00:
                self.dcmotor.DCMOTOR_stop()
                time.sleep(0.5)
            else:
                self.dcmotor.DCMOTOR_forward()
                time.sleep(0.5)

