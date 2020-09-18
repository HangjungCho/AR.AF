# I2C_ClassLib.py
import smbus2 as I2C
import time

################### I2C_Base
class I2C_Base:
    def __init__( self, slave, bus = 1 ):
        self.bus = I2C.SMBus( bus )
        self.I2C_setSlave( slave )

    def I2C_setSlave( self, slave ):
        self.slave = slave


################### LIGHT
class LIGHT( I2C_Base ):
    POWER_DOWN = 0x00       # No active state
    POWER_ON = 0x01         # Power on
    RESET = 0x07            # Reset data register value

    measureDict = { 'CONTINUOUS_LOW_RES_MODE':0x13,
                    'CONTINUOUS_LOW_RES_MODE1':0x10,
                    'CONTINUOUS_LOW_RES_MODE2':0x11,
                    'ONE_TIME_HIGH_RES_MODE1':0x20,
                    'ONE_TIME_HIGH_RES_MODE2':0x21,
                    'ONE_TIME_HIGH_RES_MODE':0x23
                  }

    def __init__( self, slave, bus = 1 ):
        super().__init__( slave, bus )
        self.LIGHT_reset()

    def LIGHT_reset( self ):
        self.bus.write_byte( self.slave, self.RESET )
        time.sleep( 0.05 )

    def Light_powerOn( self ):
        self.bus.write_byte( self.slave, self.POWER_ON )
        time.sleep( 0.05 )

    def Light_powerOff( self ):
        self.bus.write_byte( self.slave, self.POWER_OFF )
        time.sleep( 0.05 )

    def LIGHT_readLight( self, measure ):
        self.data = self.bus.read_i2c_block_data( self.slave, self.measureDict[ measure ], 2 )
        return self.LIGHT_convertToNumber()

    def LIGHT_convertToNumber( self ):
        # Simple function to convert 2 bytes of data
        # into a decimal number
        return ( ( self.data[1] + ( 256 * self.data[0] ) ) / 1.2 )


################### TEMPERATURE/HUMIDITY
class TEMP_HUMI( I2C_Base ):
    SOFT_RESET = 0xFE
    COMMAND_TEMP = 0xF3
    COMMAND_HUMI = 0xF5

    data = [ 0, 0 ]

    def __init__( self, slave, bus = 1 ):
        super().__init__( slave, bus )
        self.TEMP_HUMI_reset()

    def TEMP_HUMI_reset( self ):
        self.bus.write_byte( self.slave, self.SOFT_RESET )
        time.sleep( 0.05 )

    def TEMP_HUMI_commandTemp( self ):
        self.bus.write_byte( self.slave, self.COMMAND_TEMP )
        time.sleep( 0.260 )
        self.TEMP_HUMI_measure()

    def TEMP_HUMI_commandHumi( self ):
        self.bus.write_byte( self.slave, self.COMMAND_HUMI )
        time.sleep( 0.260 )
        self.TEMP_HUMI_measure()

    def TEMP_HUMI_measure( self ):
        for i in range( 0, 2, 1 ):
            self.data[i] = self.bus.read_byte( self.slave )

        self.val = self.data[0] << 8 | self.data[1]

    def TEMP_HUMI_getTemperature( self ):
        self.tempValue = -46.85 + 175.72 / 65536 * self.val
        return self.tempValue

    def TEMP_HUMI_getHumidity( self ):
        self.humiValue = -6.0 + 125.0 / 65536 * self.val
        return self.humiValue


################### FND
class FND( I2C_Base ):
    CMD_CONFIG = 0x06
    CMD_OUT = 0x02

    numbers = { 0:0xFC, 1:0x60, 2:0xDA, 3:0xF2, 4:0x66, 5:0xB6, 6:0x3E, 7:0xE0, 8:0xFE, 9:0xF6, 10:0x01 }
    positions = { 0:0x7F, 1:0xBF, 2:0xDF, 3:0xEF, 4:0xF7, 5:0xFB }

    def __init__( self, slave, bus = 1 ):
        super().__init__( slave, bus )
        self.FND_config()

    def FND_config( self ):
        self.bus.write_word_data( self.slave, self.CMD_CONFIG, 0x0000 )

    def FND_print_one_number( self, position, number ):
        self.number = self.numbers[ number ] << 8 | self.positions[ position ]
        self.bus.write_word_data( self.slave, self.CMD_OUT, self.number )

    def FND_print_multi_number( self, numbers ):
        for i in range( len( numbers ) ):
            self.FND_print_one_number( i, int( numbers[i] ) )
            time.sleep( 0.001 )

    def FND_print_multi_number_time( self, numbers, timeValue ):
        for i in range( len( numbers ) ):
            self.FND_print_one_number( i, int( numbers[i] ) )
            time.sleep( timeValue )
