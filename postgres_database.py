import psycopg2

host = "localhost"
user = "postgres"
dbname = "stock"
password = "emote164"
port = "9003"

conn_string = "host={0} user={1} dbname={2} password={3} port={4}".format(host, user, dbname, password, port)

try:
    conn = psycopg2.connect(conn_string)
    print("Connection established")
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS opt10059schema.table_035420(date_info integer PRIMARY KEY, curr_money integer NOT NULL, updown_icon integer NOT NULL, indi_holder integer NOT NULL, orga_holder integer NOT NULL, forg_holder integer NOT NULL, finance_holder integer NOT NULL, insurance_holder integer NOT NULL, tusin_holder integer NOT NULL, bank_holder integer NOT NULL, etcFinance_holder integer NOT NULL, yeongi_holder integer NOT NULL, samofund_holder integer NOT NULL, country_holder integer NOT NULL, etcLaw_holder integer NOT NULL, naeforg_holder integer NOT NULL);")


    #[date_info, curr_money, updown_icon, indi_holder, orga_holder, forg_holder, finance_holder, insurance_holder, tusin_holder, bank_holder, etcFinance_holder, yeongi_holder, samofund_holder, country_holder, etcLaw_holder, naeforg_holder]
    #cursor.execute("INSERT INTO opt10059schema.table_035420(date_info, curr_money, updown_icon, indi_holder, orga_holder, forg_holder, finance_holder, insurance_holder, tusin_holder, bank_holder, etcFinance_holder, yeongi_holder, samofund_holder, country_holder, etcLaw_holder, naeforg_holder) VALUES(" + date_info + "," + curr_money + "," + updown_icon + "," + indi_holder + "," + orga_holder + "," + forg_holder + "," + finance_holder + "," + insurance_holder + "," + tusin_holder + "," + bank_holder + "," + etcFinance_holder + "," + yeongi_holder + "," + samofund_holder + "," + country_holder + "," + etcLaw_holder + "," + naeforg_holder + ");")



    #cursor.execute("INSERT INTO opt10059schema.table_ahs(datee) VALUES(123);")
    #cursor.execute("INSERT INTO opt10059schema.table_ahs(datee) VALUES(231);")

    #cursor.execute("SELECT * FROM opt10059schema.table_ahc;")


    #result = cursor.fetchall()  # type : list
    #print(result)

except Exception as e:
    print("error")
    print(e)

conn.commit()
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