#opt90003 : 프로그램순매수상위50요청
#부가설명 : 코스피 또는 코스닥 각각의 프로그램 매수상위 싹다 조회하는 코드

import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
import time

class Program(QMainWindow):

    def __init__(self):
        super().__init__()
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom.dynamicCall("CommConnect()")  # 로그인창 호출

        # 서버로부터 오는 이벤트에 콜백함수 등록
        self.kiwoom.OnEventConnect.connect(self.receiveLoginEvent)
        self.kiwoom.OnReceiveTrData.connect(self.receiveTrData)

    # 로그인창에서 아이디와 패스워드가 맞으면 불리는 함수
    def receiveLoginEvent(self, err_code):
        if err_code == 0:
            print("로그인 성공")
            self.requestTrData(0)  # 로그인 성공이 확인된 후에만 요청을 할 수 있다.

    def requestTrData(self, c):
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "매매상위구분", "2")  # 1: 순매도상위, 2: 순매수상위
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "금액수량구분", "1")  # 1: 금액, 2: 수량
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "시장구분", "P00101")  # P00101: 코스피, P10102: 코스닥
            self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "opt90003_req", "opt90003", c, "0766") # 사용사요청명칭 / 요청함수 / 초기조회:0, 연속조회:2 / 화면번호

    def receiveTrData(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        if rqname == "opt90003_req":
            for i in range(100):
                rank = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "순위")
                if(rank == ""):
                    break
                code = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "종목코드")
                name = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "종목명")
                price = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "현재가")
                symbol = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "등락기호")     # 2:+, 3:0, 5:-
                percent = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "등락율")      # ex) +2.10, 0.00, -7.00
                volume = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "누적거래량")
                sell = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "프로그램매도금액")
                buy = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "프로그램매수금액")
                pureBuy = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "프로그램순매수금액")
                print(rank.strip(), "\t", code.strip(), "\t", name.strip(), "\t", price.strip(), "\t", symbol.strip(), "\t", percent.strip(), "\t", volume.strip(), "\t", sell.strip(), "\t", buy.strip(), "\t", pureBuy.strip())

            if(prev_next == '2'):       # 추가로 조회할게 존재한다면 2, 없다면 0이므로
                time.sleep(0.15)        # !이 딜레이를 없애면 초당 요청 블락에 걸려서 전체 조회가 되지 않는다.!
                self.requestTrData(2)   #연속조회
            else:
                print("조회완료")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    trace = Program()
    app.exec_()