import psycopg2

host = "localhost"
user = "postgres"
dbname = "stockdb"      #사용할 데이터베이스 이름
password = "emote164"   #설치할 때 지정한 것
port = "9003"           #설치할 때 지정할 것

conn_string = "host={0} user={1} dbname={2} password={3} port={4}".format(host, user, dbname, password, port)

try:
    #데이터 베이스를 연결하고 db를 선택해줌
    conn = psycopg2.connect(conn_string)
    print("연결성공")

    cursor = conn.cursor()

    #스키마 생성
    cursor.execute("create SCHEMA IF NOT EXISTS stock_code;")
    cursor.execute("create SCHEMA IF NOT EXISTS stock_daily;")
    cursor.execute("create SCHEMA IF NOT EXISTS stock_weekly;")
    cursor.execute("create SCHEMA IF NOT EXISTS stock_monthly;")


    #stock_code스키마 하위에 kospi, kosdaq 테이블을 생성
    cursor.execute("create TABLE IF NOT EXISTS stock_code.kospi(code varchar(6) NOT NULL PRIMARY KEY, name varchar(20) NOT NULL);")
    cursor.execute("create TABLE IF NOT EXISTS stock_code.kosdaq(code varchar(6) NOT NULL PRIMARY KEY, name varchar(20) NOT NULL);")





    #cursor.execute("INSERT INTO opt10059schema.table_035420(date_info, curr_money) VALUES(" + date_info + "," + curr_money + ");")



    #cursor.execute("INSERT INTO opt10059schema.table_ahs(datee) VALUES(123);")
    #cursor.execute("INSERT INTO opt10059schema.table_ahs(datee) VALUES(231);")

    #cursor.execute("SELECT * FROM opt10059schema.table_ahc;")


    #result = cursor.fetchall()  # type : list
    #print(result)

except Exception as e:
    print("error")
    print(e)

conn.commit()   #이게 없으면 실제로 반영이 안됨.
cursor.close()
conn.close()

# \l                                 # 데이터베이스 목록 확인하기
# \c 데이터베이스명                    # 데이터베이스 변경하기
# CREATE DATABASE 데이터베이스명;      # 데이터베이스 생성

# \dn                                # 스키마 리스트를 보여준다.
# CREATE SCHEMA 스키마명              # 스키마를 생성한다.

# \dt 스키마이름.*                    # 해당 스키마가 가지고 있는 테이블리스트를 보여준다.
# \d 스키마이름.테이블이름              # 테이블 속성의 데이터형을 보여준다.

# cursor.execute("CREATE TABLE opt10059schema.table_035420(date varchar(20) )")
# cursor.execute("INSERT INTO opt10059schema.table_035420(id, pw) VALUES('12a','asdqq');")
# cursor.execute("SELECT * FROM opt10059schema.table_035420;")