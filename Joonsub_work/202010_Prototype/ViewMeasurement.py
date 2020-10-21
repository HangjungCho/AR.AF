# sensor_NET_Monitor_ClassLib.py
import sqlite3
import sys

def main_menu():
    menu = '''
    1. 전체 제품 수량 현황 정보 조회
    2. 특정 제품 수량 현황 정보 조회
    0. 종료
    select menu : '''
    while True:
        print( menu, end = ' ' )
        selectMenu = input()
        try:
            if int(selectMenu) == 1:
                viewMeasurement(selectMenu)
            elif int(selectMenu) == 2:
                viewType()
            elif int(selectMenu) == 0:
                break
        except:
            print('잘못된 입력입니다. 다시 입력해 주세요')
            continue

def viewMeasurement( index ):
    conn = sqlite3.connect( 'araf.db' )

    try :
        with conn:
            cursor = conn.cursor()
            cursor.execute( 'SELECT * FROM Count ')
            print()
            for row in cursor.fetchall(): 
                # print( '{0:3} {1:3}'.format( row[1], row[2]) )
                print( '\t제품 번호 : {}, 재고 수량 : {}'.format(row[0], row[1]) )

    except FileNotFoundError:
        pass

    finally:
        conn.close()
    return

def viewType():
    conn = sqlite3.connect( 'araf.db' )

    try :
        while True:
            menu2 = '''
        1. 원하는 제품 명 입력하세요.
        0. 종료
        select menu : '''
            print( menu2, end = ' ' )
            viewmenu = input()
            if int(viewmenu) == 0:
                break
            with conn:
                cursor = conn.cursor()
                cursor.execute( 'SELECT * FROM Quantity WHERE type = ? ', ( viewmenu ))
                print()
                for row in cursor.fetchall(): 
                    # print( '{0:3} {1:3}'.format( row[1], row[2]) )
                    print( '\t제품 번호 : {}, 제품 ADD/REVERT : {}, 제품 수량 : {}, 제품입고 날자 및 시간 : {} {}'.format(row[1], row[2],row[3], row[4], row[5]))
                    #print(row)

    except FileNotFoundError:
        print('제품이 없습니다.')

    except:
        print('잘못된 입력입니다. 다시 입력해 주세요')

    finally:
        conn.close()

if __name__ == '__main__':
    main_menu()