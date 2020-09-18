# sensor_NET_GPIO_ClassLib.py
from multiprocessing import Process, Queue
from GPIO_ClassLib import LED
from GPIO_ClassLib import DCMOTOR
from GPIO_ClassLib import USONIC
import time

class LEDProcess( Process ):
    def __init__( self, ledCmdQueue ):
        Process.__init__( self, name = "LEDProcess" )

        self.ports = ( 14, 15 )
        self.led_state = { 1:False, 2:False }
        self.led_brightness_state = { 1:False }
        self.led_brightness = [ 0.0 ]

        self.led = LED( self.ports, ( 'out', 'out' ) )

        self.led.LED_output( ( True, True ))
        time.sleep( 0.5 )
        self.led.LED_output( ( self.led_state[1], self.led_state[2] ) )

        self.commandQueue = ledCmdQueue

        print( '[LEDProcess __init__]' )

    def __del__( self ):
        print( '[LEDProcess __del__]' )

    def run( self ):
        try:
            loop = True

            while loop:
                print( "LED Looping..." )
                operation = self.commandQueue.get()

                if operation == 'LD1ON':
                    print( "LED:LED 1 On" )
                    self.pwm_stop()
                    self.led_state[1] = True
                elif operation == 'LD2ON':
                    print( "LED:LED 2 On" )
                    self.led_state[2] = True
                elif operation == 'LD1OF':
                    print( "LED:LED 1 Off" )
                    self.pwm_stop()
                    self.led_state[1] = False
                elif operation == 'LD2OF':
                    print( "LED:LED 2 Off" )
                    self.led_state[2] = False
                elif operation == 'LD_ON':
                    print( "LED:LED On" )
                    self.pwm_stop()
                    self.led_state[1] = True
                    self.led_state[2] = True
                elif operation == 'LDOFF':
                    print( "LED:LED Off" )
                    self.pwm_stop()
                    self.led_state[1] = False
                    self.led_state[2] = False
                elif operation == 'LD1UP':
                    print( "LED:LED 1 Up" )
                    self.pwm_init()

                    self.led_brightness[0] += 10.0
                    if self.led_brightness[0] >= 100.0:
                        self.led_brightness[0] = 100.0
                    self.led.GPIO_PWM_ChangeDutyCycle( self.led_brightness[0] )
                elif operation == 'LD1DN':
                    print( "LED:LED 1 Dn" )
                    self.pwm_init()

                    self.led_brightness[0] -= 10.0
                    if self.led_brightness[0] <= 0.0:
                        self.led_brightness[0] = 0.0
                    self.led.GPIO_PWM_ChangeDutyCycle( self.led_brightness[0] )

                print( "LED:LED process....." )
                self.led.LED_output( ( self.led_state[1], self.led_state[2] ) )

        except ( RuntimeError ):
            print( "Runtime Error" )

    def pwm_init( self ):
        if self.led_brightness_state[1] == False:
            self.led_brightness_state[1] = True
            self.led.PWM_setup( self.ports[0], 100.0 )
            self.led.PWM_start( 0.0 )

    def pwm_stop( self ):
        if self.led_brightness_state[1] == True:
            self.led.PWM_stop()
            self.led_brightness_state[1] = False

class DCMotorProcess( Process ):
    def __init__( self, dcmotorCmdQueue ):
        Process.__init__( self, name = "DCMotorProcess" )

        self.ports = ( 4, 25, 12 )
        self.motor_speed = 50.0

        self.motor = DCMOTOR( self.ports, ( 'out', 'out', 'out' ) )
        self.motor.GPIO_PWM_setup( self.ports[2], 100.0 )


        self.commandQueue = dcmotorCmdQueue

        print( '[DCMotorProcess __init__]' )

    def __del__( self ):
        print( '[DCMotorProcess __del__]' )

    def run( self ):
        try:
            loop = True

            while loop:
                print( "DC Motor Looping..." )
                operation = self.commandQueue.get()

                print( "DC Motor:DC Motor process....." )
                if operation == 'MTRFR':
                    print( "DC Motor:DC Motor forward" )
                    self.motor.GPIO_PWM_start( self.motor_speed )
                    self.motor.DCMOTOR_forward()
                    time.sleep( 0.5 )
                elif operation == 'MTRBC':
                    print( "DC Motor:DC Motor backward" )
                    self.motor.GPIO_PWM_start( self.motor_speed )
                    self.motor.DCMOTOR_backward()
                    time.sleep( 0.5 )
                elif operation == 'MTRUP':
                    print( "DC Motor:DC Motor speed up" )
                    self.motor_speed += 10.0
                    if self.motor_speed >= 100.0:
                        self.motor_speed = 100.0

                    self.motor.GPIO_PWM_ChangeDutyCycle( self.motor_speed )
                    time.sleep( 0.5 )
                elif operation == 'MTRDN':
                    print( "DC Motor:DC Motor speed down" )
                    self.motor_speed -= 10.0
                    if self.motor_speed <= 0.0:
                        self.motor_speed = 0

                    self.motor.GPIO_PWM_ChangeDutyCycle( self.motor_speed )
                    time.sleep( 0.5 )

                elif operation == 'MTRST':
                    print( "DC Motor:DC Motor stop" )
                    self.motor.GPIO_PWM_stop()
                    self.motor.DCMOTOR_stop()

        except ( RuntimeError ):
            print( "Runtime Error" )

class USonicProcess( Process ):
    def __init__( self, usonicCmdQueue, usonicRstQueue ):
        Process.__init__( self, name = "USonicProcess" )

        self.ports = ( 0, 1 )
        self.direction = ( 'out', 'in' )

        self.usonic = USONIC( self.ports, self.direction )

        self.commandQueue = usonicCmdQueue
        self.resultQueue = usonicRstQueue

        print( '[USonicProcess __init__]' )

    def __del__( self ):
        print( '[USonicProcess __del__]' )

    def run( self ):
        try:
            loop = True

            print( "Ultrasonic:UltraSonic looping....." )
            while loop:
                print( "Ultrasonic:UltraSonic process....." )
                operation = self.commandQueue.get()
                print( "operation {0}".format( operation ) )
                if operation == 'MEASU':
                    self.usonic.USONIC_send()
                    self.usonic.USONIC_receive()
                    distance = str( 'Distance : {0:5.2f} cm'.format( self.usonic.USONIC_getDistance() ) )
                    print( distance )
                    self.resultQueue.put( distance )

        except ( RuntimeError ):
            print( "Runtime Error" )
