# GPIO_ClassLib.py
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


################### LED
class LED( GPIO_Base ):
    ports = []

    def __init__( self, ports, direction ):
        for i in range( len( ports ) ):
            self.ports.append( ports[i] )

        super().__init__( ports, direction )

    def LED_output( self, outValues ):
        i = 0
        for port in self.ports:
            GPIO.output( port, outValues[i] )
            i += 1

    def PWM_setup( self, port, startDuty ):
        super().GPIO_PWM_setup( port, startDuty )

    def PWM_start( self, duty ):
        super().GPIO_PWM_start( duty )

    def PWM_operation( self, start, stop, interval ):
        super().GPIO_PWM_operation( start, stop, interval )

    def PWM_stop( self ):
        super().GPIO_PWM_stop()


################### JOGSW
class JOGSW( GPIO_Base ):
    ports = []

    def __init__( self, ports, direction ):
        for i in range( len( ports ) ):
            self.ports.append( ports[i] )

        super().__init__( ports, direction )

    def JOGSW_input( self ):
        while True:
            for jog in self.ports:
                jog_stat = GPIO.input( jog )
                if jog_stat == 1:
                    return jog, jog_stat

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


################### PIEZO
class PIEZO( GPIO_Base ):
    ports = []
    directions = []
    scales = { 1:{ 'C':33,   'D':37,   'E':41,   'F':44,   'G':48,   'A':55,   'B':61 },
               2:{ 'C':65,   'D':73,   'E':82,   'F':87,   'G':98,   'A':110,  'B':123 },
               3:{ 'C':131,  'D':146,  'E':165,  'F':174,  'G':195,  'A':220,  'B':247 },
               4:{ 'C':262,  'D':294,  'E':330,  'F':349,  'G':391,  'A':440,  'B':494 },
               5:{ 'C':523,  'D':587,  'E':659,  'F':698,  'G':784,  'A':880,  'B':987 },
               6:{ 'C':1047, 'D':1175, 'E':1319, 'F':1397, 'G':1568, 'A':1760, 'B':1976 },
               7:{ 'C':2093, 'D':2349, 'E':2637, 'F':2794, 'G':3135, 'A':3520, 'B':3951 },
               8:{ 'C':4189, 'D':4699, 'E':5274, 'F':5588, 'G':6272, 'A':7040, 'B':7902 }
            }

    def __init__( self, port, direction ):
        self.ports.append( port )
        self.directions.append( direction )

        super().__init__( self.ports, self.directions )

    def PIEZO_play_setup( self, setupDuty, startDuty, changeDuty ):
        super().GPIO_PWM_setup( self.ports[0], startDuty )
        super().GPIO_PWM_start( startDuty )
        super().GPIO_PWM_ChangeDutyCycle( changeDuty )

    def PIEZO_play( self, scale ):
        super().GPIO_PWM_ChangeFrequency( self.scales[ scale[0] ][ scale[1].upper() ] );

    def PIEZO_plays( self, scales, timeValue ):
        for scale in scales:
            print( scale )
            super().GPIO_PWM_ChangeFrequency( self.scales[ scale[0] ][ scale[1].upper() ] );
            time.sleep( timeValue )

    def PIEZO_play_stop( self ):
        super().GPIO_PWM_stop()


################### CLCD
class CLCD( GPIO_Base ):
    port_dicts = { 'LCD_RS':23, 'LCD_RW':24, 'LCD_E':26,
                   'LCD_D4':17, 'LCD_D5':18, 'LCD_D6':27, 'LCD_D7':22 }
    ports = ( 23, 24, 26, 17, 18, 27, 22 )
    directions = ( 'out', 'out', 'out', 'out', 'out', 'out', 'out' )

    LCD_WIDTH = 16
    LCD_CHR = True
    LCD_CMD = False

    LCD_LINE1 = 0x80
    LCD_LINE2 = 0xC0

    E_PLUSE = 0.0005
    E_DELAY = 0.0005

    def __init__( self ):
        super().__init__( self.ports, self.directions )
        self.CLCD_init()

    def CLCD_init( self ):
        self.CLCD_lcd_byte( 0x33, self.LCD_CMD )       # 110011 Initialize, LCD Chip 4bit 사용을 위한 초기화 명령
        self.CLCD_lcd_byte( 0x32, self.LCD_CMD )       # 110010 Initialize, LCD Chip 4bit 사용을 위한 초기화 명령

        self.CLCD_lcd_byte( 0x06, self.LCD_CMD )       # 000110 Cursor move direction
        self.CLCD_lcd_byte( 0x0c, self.LCD_CMD )       # 001100 Display On, Cursor Off, Blink Off
        self.CLCD_lcd_byte( 0x28, self.LCD_CMD )       # 101000 Data length, number of lines, font size
        self.CLCD_lcd_clear()                          # 000001 Clear display
        time.sleep( self.E_DELAY )

    def CLCD_lcd_byte( self, bits, mode ):
        GPIO.output( self.port_dicts[ 'LCD_RS' ], mode )

        GPIO.output( self.port_dicts[ 'LCD_D4' ], False )
        GPIO.output( self.port_dicts[ 'LCD_D5' ], False )
        GPIO.output( self.port_dicts[ 'LCD_D6' ], False )
        GPIO.output( self.port_dicts[ 'LCD_D7' ], False )

        if bits & 0x10 == 0x10:
            GPIO.output( self.port_dicts[ 'LCD_D4' ], True )

        if bits & 0x20 == 0x20:
            GPIO.output( self.port_dicts[ 'LCD_D5' ], True )

        if bits & 0x40 == 0x40:
            GPIO.output( self.port_dicts[ 'LCD_D6' ], True )

        if bits & 0x80 == 0x80:
            GPIO.output( self.port_dicts[ 'LCD_D7' ], True )

        self.CLCD_lcd_toggle_enable()

        GPIO.output( self.port_dicts[ 'LCD_D4' ], False )
        GPIO.output( self.port_dicts[ 'LCD_D5' ], False )
        GPIO.output( self.port_dicts[ 'LCD_D6' ], False )
        GPIO.output( self.port_dicts[ 'LCD_D7' ], False )

        if bits & 0x01 == 0x01:
            GPIO.output( self.port_dicts[ 'LCD_D4' ], True )

        if bits & 0x02 == 0x02:
            GPIO.output( self.port_dicts[ 'LCD_D5'], True )

        if bits & 0x04 == 0x04:
            GPIO.output( self.port_dicts[ 'LCD_D6' ], True )

        if bits & 0x08 == 0x08:
            GPIO.output( self.port_dicts[ 'LCD_D7' ], True )

        self.CLCD_lcd_toggle_enable()

    def CLCD_lcd_toggle_enable( self ):
        time.sleep( self.E_DELAY )
        GPIO.output( self.port_dicts[ 'LCD_E' ], True )
        time.sleep( self.E_PLUSE )
        GPIO.output( self.port_dicts[ 'LCD_E' ], False )
        time.sleep( self.E_DELAY )

    def CLCD_lcd_clear( self ):
        self.CLCD_lcd_byte( 0x01, self.LCD_CMD )

    def CLCD_lcd_write( self, message, line ):
        if line == 1 :
            self.lineNumber = self.LCD_LINE1
        elif line == 2:
            self.lineNumber = self.LCD_LINE2

        if 1 <= line <= 2:
            message = message.ljust( self.LCD_WIDTH, " " )
            self.CLCD_lcd_byte( self.lineNumber, self.LCD_CMD )

            for i in range( self.LCD_WIDTH ):
                self.CLCD_lcd_byte( ord( message[i] ), self.LCD_CHR )

            return 1
        else:
            return -1


################### USONIC
class USONIC( GPIO_Base ):
    ports = {}
    portname = ( 'TRIG', 'ECHO' )

    def __init__( self, ports, direction ):
        self.ports[ 'TRIG' ] = ports[0]
        self.ports[ 'ECHO' ] = ports[1]

        super().__init__( ports, direction )

    def USONIC_send( self ):
        GPIO.output( self.ports[ 'TRIG' ], False )
        time.sleep( 0.5 )

        GPIO.output( self.ports[ 'TRIG' ], True )
        time.sleep( 0.00001 )
        GPIO.output( self.ports[ 'TRIG' ], False )

    def USONIC_receive( self ):
        while GPIO.input( self.ports[ 'ECHO' ] ) == False:
            self.pulse_start = time.time()

        while GPIO.input( self.ports[ 'ECHO' ] ) == True:
            self.pulse_end = time.time()

        self.pulse_duration = self.pulse_end - self.pulse_start
        self.distance = self.pulse_duration * 17000
        self.distance = round( self.distance, 2 )

    def USONIC_getDistance( self ):
        return self.distance


################### PIR
class PIR( GPIO_Base ):
    ports = []
    directions = []

    def __init__( self, port, direction ):
        self.ports.append( port )
        self.directions.append( direction )

        super().__init__( self.ports, self.directions )

    def PIR_motionDetection( self ):
        self.detection = GPIO.input( self.ports[0] )

        return self.detection
