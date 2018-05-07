#opt10059 : 종목별투자자기관별요청
#부가설명 : 어느 한 종목의 매수주체에 대한 세부 정보 조회

import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
import time
from datetime import datetime
from pandas import DataFrame
import psycopg2

class Program(QMainWindow):

    def __init__(self):
        super().__init__()
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom.dynamicCall("CommConnect()")  # 로그인창 호출

        # 서버로부터 오는 이벤트에 콜백함수 등록
        self.kiwoom.OnEventConnect.connect(self.receiveLoginEvent)
        self.kiwoom.OnReceiveTrData.connect(self.receiveTrData)
        self.df = DataFrame(columns=("date_info", "curr_money", "updown_icon", "indi_holder", "orga_holder", "forg_holder", "finance_holder", "insurance_holder", "tusin_holder", "bank_holder", "etcFinance_holder", "yeongi_holder", "samofund_holder", "country_holder", "etcLaw_holder", "naeforg_holder"))
        self.df_lastIndex = 0
        self.cursor = self.makeConnectDB().cursor()
        self.currentItemCode = "035420" # 조회할 종목
        
        
        
    # 로그인창에서 아이디와 패스워드가 맞으면 불리는 함수
    def receiveLoginEvent(self, err_code):
        if err_code == 0:
            print("로그인 성공")
            self.requestTrData(0, self.currentItemCode)  # 로그인 성공이 확인된 후에만 요청을 할 수 있다.

    def requestTrData(self, c, currentItemCode):
        today = self.getToday()
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "일자", today) # 오늘의 날짜를 입력하면 된다.
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", self.currentItemCode) # 035420: 네이버
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "금액수량구분", "2")  # 1: 금액, 2: 수량
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "매매구분", "0")  # 0: 순매수, 1: 매수, 2: 매도
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "단위구분", "1")  # 1000: 천주, 1: 단주
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10059_req", "opt10059", c, "0766") # 사용사요청명칭 / 요청함수 / 초기조회:0, 연속조회:2 / 화면번호

    def receiveTrData(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        if rqname == "opt10059_req":
            for i in range(100):
                date_info = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "",rqname, i, "일자").strip()
                if(date_info == ""):
                    break
                curr_money = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "현재가").strip().replace('+', '')      #+80000
                curr_money = curr_money.replace('-', '')
                updown_icon = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "대비기호").strip()    # 2: +, 5: -
                indi_holder = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode,"", rqname, i, "개인투자자").strip()
                orga_holder = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "기관계").strip()
                forg_holder = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode,"", rqname, i, "외국인투자자").strip()
                finance_holder = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode,"", rqname, i, "금융투자").strip()
                insurance_holder = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)",trcode, "",rqname, i, "보험").strip()
                tusin_holder = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode,"",rqname, i, "투신").strip()
                bank_holder = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode,"", rqname, i, "은행").strip()
                etcFinance_holder = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)",trcode, "",rqname, i, "기타금융").strip()
                yeongi_holder = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode,"",rqname, i, "연기금등").strip()
                samofund_holder = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)",trcode, "",rqname, i, "사모펀드").strip()
                country_holder = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode,"",rqname, i, "국가").strip()
                etcLaw_holder = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "",rqname, i, "기타법인").strip()
                naeforg_holder = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode,"",rqname, i, "내외국인").strip()

                self.df.loc[self.df_lastIndex] = [date_info, curr_money, updown_icon, indi_holder, orga_holder, forg_holder, finance_holder, insurance_holder, tusin_holder, bank_holder, etcFinance_holder, yeongi_holder, samofund_holder, country_holder, etcLaw_holder, naeforg_holder]
                self.df_lastIndex = self.df_lastIndex + 1

                print(date_info, "\t", curr_money, "\t", updown_icon, "\t", indi_holder, "\t", orga_holder, "\t", forg_holder, "\t", finance_holder, "\t", insurance_holder, "\t", \
                      tusin_holder, "\t", bank_holder, "\t", etcFinance_holder, "\t", yeongi_holder, "\t", samofund_holder, "\t", country_holder, "\t", etcLaw_holder, "\t", naeforg_holder)

            if(prev_next == '2'):       # 추가로 조회할게 존재한다면 2, 없다면 0이므로
                time.sleep(0.15)        # !이 딜레이를 없애면 초당 요청 블락에 걸려서 전체 조회가 되지 않는다.!
                self.requestTrData(2, self.currentItemCode)   #연속조회
            else:
                print("조회완료")
                print(self.df)
                self.cursor.execute("CREATE TABLE IF NOT EXISTS opt10059schema.table_" + self.currentItemCode + "(date_info integer PRIMARY KEY, curr_money integer NOT NULL, updown_icon integer NOT NULL, indi_holder integer NOT NULL, orga_holder integer NOT NULL, forg_holder integer NOT NULL, finance_holder integer NOT NULL, insurance_holder integer NOT NULL, tusin_holder integer NOT NULL, bank_holder integer NOT NULL, etcFinance_holder integer NOT NULL, yeongi_holder integer NOT NULL, samofund_holder integer NOT NULL, country_holder integer NOT NULL, etcLaw_holder integer NOT NULL, naeforg_holder integer NOT NULL);")

                ## 여기에서 self.requestTrData(0, 다음종목코드) 를 불러주면 다음 종목코드의 데이터를 받아온다.

    def getToday(self):
        todayYear = str(datetime.today().year)
        todayMonth = datetime.today().month
        todayDay = str(datetime.today().day)

        if (todayMonth < 10):
            todayMonth = '0' + str(datetime.today().month)

        return todayYear + todayMonth + todayDay

    def makeConnectDB(self):
        host = "localhost"
        user = "postgres"
        dbname = "stock"
        password = "emote164"
        port = "9003"
        conn_string = "host={0} user={1} dbname={2} password={3} port={4}".format(host, user, dbname, password, port)

        try:
            conn = psycopg2.connect(conn_string)
            print("Connection established")
        except Exception as e:
            print(e)

        return conn


if __name__ == "__main__":
    app = QApplication(sys.argv)
    trace = Program()
    app.exec_()
