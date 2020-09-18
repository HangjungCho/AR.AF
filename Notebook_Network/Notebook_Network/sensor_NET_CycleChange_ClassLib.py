# sensor_NET_CycleChange_ClassLib.py
import sqlite3
import sys
import time, datetime

class SensorMeasureCycle:
    def __init__( self ):
        self.sensorKind = { 1:( 'UltraSonic', 'MEASU' ), 2:( 'Temperature/Humidity', 'TEMHU'),
                            3:( 'Light', 'LIGHT' ) }

    def main_menu( self ):
        menu = '''
1. UltraSonic Sensor Measure 주기 변경
2. Temperature/Humidity Sensor Measure 주기 변경
3. Light Sensor Measure 주기 변경
4. Sensor Measure 주기 정보 조회
0. 종료
select menu : '''

        while True:
            print( menu, end = ' ' )
            selectMenu = int( input() )

            if selectMenu == 0:
                break
            elif 1 <= selectMenu <= 3:
                self.sensorCycleChange( selectMenu )
            elif 4 == selectMenu:
                self.sensorCycleChangeInfo()
        return

    def sensorCycleChange( self, kind ):
        cycleValue = int( input( '{0} sensor 측정 주기( 1 ~ 120 ) : '.format( self.sensorKind[ kind ][0] ) ) )
        while ( cycleValue < 1 or cycleValue  > 120 ):
            print( '{0} sensor 측정 주기는 1 ~ 120 사이만 가능합니다.'.format( self.sensorKind[ kind ][0] ))
            cycleValue = int( input( '{0} sensor 측정 주기( 1 ~ 120 ) : '.format( self.sensorKind[ kind ][0] ) ) )

        now = datetime.datetime.now()
        date = now.strftime( '%Y-%m-%d' )
        time = now.strftime( '%H:%M:%S' )
        data = self.sensorKind[kind][1], cycleValue, date, time

        conn = sqlite3.connect( 'sensorinfo.db' )
        with conn:
            cursor = conn.cursor()
            cursor.execute( 'INSERT INTO sensor_info( kind, value, date, time ) VALUES ( ?, ?, ?, ? )', data )
            conn.commit()

        print( '{0} Sensor Measure Cycle insert complete...\n'.format( self.sensorKind[ kind ][0] ) )
        return

    def sensorCycleChangeInfo( self ):
        conn = sqlite3.connect( 'sensorinfo.db' )

        print()
        with conn:
            cursor = conn.cursor()
            cursor.execute( 'SELECT * FROM sensor_info' )
            for row in cursor.fetchall():
                print( '{0:5} {1:>5} {2} {3:10} {4:8}'.format( row[1], row[2], row[3], row[4], row[5] ) )
        input( 'Press any key..............' )
        return

if __name__ == '__main__':
    sensorMeasureCycle = SensorMeasureCycle()
    sensorMeasureCycle.main_menu()
