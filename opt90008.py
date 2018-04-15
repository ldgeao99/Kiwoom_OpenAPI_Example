#opt90008 : 종목시간별프로그램매매추이요청
#부가설명 : 입력한 날짜 하루동안의 프로그램이 매매한 내역을 알 수 있으며 (000000)시간,분,초 단위로 보여진다.

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
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "시간일자구분", "1")   # 오직 1만 가능
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "금액수량구분", "1")   # 1: 금액, 2: 수량
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", "035420")  # 종목코드
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "날짜", "20180118")   # 조회할 날짜
            self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "opt90008_req", "opt90008", c, "0766") # 사용사요청명칭 / 요청함수 / 초기조회:0, 연속조회:2 / 화면번호

    def receiveTrData(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        if rqname == "opt90008_req":
            print(prev_next)
            for i in range(100):
                dealTime = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "시간")
                if (dealTime == ""):
                    break
                price = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "현재가")
                symbol = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "대비기호")   # 2:+, 3:0, 5:-
                percent = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "등락율")
                volume = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "거래량")

                sellPriceAmount = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "프로그램매도금액")
                buyPriceAmount = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "프로그램매수금액")
                pureBuyPriceAmount = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "프로그램순매수금액")
                pureBuyPriceAmountChange = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "프로그램순매수금액증감")

                sellVolumeCount = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "프로그램매도수량")
                buyVolumeCount = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "프로그램매수수량")
                pureBuyVolumeCount = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "프로그램순매수수량")
                pureBuyVolumeCountChange = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "프로그램순매수수량증감")

                print(i, dealTime.strip(), "\t", price.strip(), "\t", symbol.strip(), "\t", percent.strip(), "\t", volume.strip(), "\t", sellPriceAmount.strip(), "\t", buyPriceAmount.strip(), "\t", pureBuyPriceAmount.strip(), "\t", pureBuyPriceAmountChange.strip(), "\t", sellVolumeCount.strip(), "\t", buyVolumeCount.strip(), "\t", pureBuyVolumeCount.strip(), "\t", pureBuyVolumeCountChange.strip())


            if (prev_next == '2'):
                print("연속조회")
                time.sleep(0.5)        # !이 딜레이를 없애면 초당 요청 블락에 걸려서 전체 조회가 되지 않는다.!
                self.requestTrData(2)   #연속조회
            else:
                print("조회완료")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    trace = Program()
    app.exec_()