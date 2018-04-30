#opt10079 : 주식틱차트조회요청
#부가설명 : 1, 3, 5, 10, 30틱 봉의 데이터를 각각 얻을 수 있음. 코드상으로 보면 분봉차트조회요청과 별반 다를게 없음.

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
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", "035420")  # 종목코드
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "틱범위", "1")  # 1: 1틱, 3: 3틱, 5: 5틱, 10: 10틱, 30: 30틱
            self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "0")   # 0 or 1, 1: 유상증자, 2: 무상증자, 4: 배당락, 8: 액면불할, 16: 액면병합, 32: 기업합병, 64: 감자, 256: 권리락
            self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10079_req", "opt10079", c, "0766") # 사용사요청명칭 / 요청함수 / 초기조회:0, 연속조회:2 / 화면번호

    def receiveTrData(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        if rqname == "opt10079_req":
            print(prev_next)
            for i in range(1000): # 한번 요청에 900개의 봉 정보가 들어오는데 혹시몰라서 큰 값으로 잡음.
                dealTime = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "체결시간")

                if (dealTime == ""):
                    break
                currentPrice = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "현재가")
                startPrice = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "시가")
                highPrice = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "고가")
                lowPrice = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "저가")
                volumeCount = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "거래량")

                print(i, dealTime.strip(), "\t", currentPrice.strip(), "\t", startPrice.strip(), "\t", highPrice.strip(), "\t", lowPrice.strip(), "\t", volumeCount.strip())

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