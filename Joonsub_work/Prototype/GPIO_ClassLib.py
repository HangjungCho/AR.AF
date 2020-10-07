# GPIO_ClassLib.py
import RPi.GPIO as GPIO
import time

################### GPIO_Base
class GPIO_Base:
    def __init__( self, ports, directions ):
        self.GPIO_setmode()

        i = 0
        for port in ports:
            if ( directions[i].upper() == 'IN' ):
                self.GPIO_init_in( port )
            else:
                self.GPIO_init_out( port )
            i += 1

    def __del__( self ):
        GPIO.cleanup()

    def GPIO_setmode( self ):
        GPIO.setwarnings( False )
        GPIO.setmode( GPIO.BCM )

    def GPIO_init_out( self, port ):
        GPIO.setup( port, GPIO.OUT )

    def GPIO_init_in( self, port ):
        GPIO.setup( port, GPIO.IN )

    def GPIO_PWM_setup( self, port, startDuty ):
        self.p = GPIO.PWM( port, startDuty )

    def GPIO_PWM_start( self, duty ):
        self.p.start( duty )

    def GPIO_PWM_operation( self, start, stop, interval ):
        for duty in range( start, stop + 1, interval ):
            self.GPIO_PWM_ChangeDutyCycle( duty )
            time.sleep( 0.2 )

    def GPIO_PWM_ChangeDutyCycle( self, duty ):
        self.p.ChangeDutyCycle( duty )

    def GPIO_PWM_ChangeFrequency( self, frequency ):
        self.p.ChangeFrequency( frequency )

    def GPIO_PWM_stop( self ):
        self.p.stop()

################### DCMOTOR
class DCMOTOR( GPIO_Base ):
    ports = {}
    portname = ( 'RP', 'RN', 'EN' )

    def __init__( self, ports, direction ):
        for i in range( len( ports ) ):
            self.ports[ self.portname[i] ] = ports[i]

        super().__init__( ports, direction )

    def DCMOTOR_forward( self ):
        GPIO.output( self.ports[ self.portname[0] ], True )
        GPIO.output( self.ports[ self.portname[1] ], False )
        GPIO.output( self.ports[ self.portname[2] ], True )

    def DCMOTOR_backward( self ):
        GPIO.output( self.ports[ self.portname[0] ], False )
        GPIO.output( self.ports[ self.portname[1] ], True )
        GPIO.output( self.ports[ self.portname[2] ], True )

    def DCMOTOR_stop( self ):
        GPIO.output( self.ports[ 'EN' ], False )


################### infrared sensor
class InfraerdSensor( GPIO_Base ):
    ports = []
    self.Check = 0

    def __init__( self, ports, direction ):
        self.ports.append( ports )

        super().__init__( ports, direction )

    def InfraerdSensor_run( self ):
        while True:
            current_state = GPIO.input(ports[0])
            if current_state != GPIO.LOW:
               self.Check = 1
            else:
                self.Check = 0
            time.sleep(0.2)

    def InfraerdSensor_getCheck( self ):
        return self.Check


################### relay module
class RelayModule( GPIO_Base ):
    ports = []

    def __init__( self, ports, direction ):
        self.ports.append( ports )

        super().__init__( ports, direction )

    def RelayModule_on( self ):
        GPIO.output( self.ports[0], True )

    def RelayModule_off( self ):
        GPIO.output( self.ports[0], False )