import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QAxContainer import *
from PyQt5 import QtCore
import queue
import time
import json
import datetime

TypeInfomation = ""


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Kiwoom Login
        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom.dynamicCall("CommConnect()")
        self.kiwoom.OnEventConnect.connect(self.event_connect)
        self.kiwoom.OnReceiveTrData.connect(self.receive_trdata)

        self.setWindowTitle("PyStock")
        self.setGeometry(600, 600, 450, 150)

        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.checkqueue)
        self.timer.setInterval(500)
        self.timer.start()

    def checkqueue(self):
        if commandQueue.qsize() > 0:
            command = commandQueue.get()
            if command == "opt10001\n":
                # print("주식 요청중...")
                while True:
                    if commandQueue.qsize() > 0:
                        break
                    else:
                        pass
                command = command.rstrip()
                # print(command)
                # print("종목코드 받아오는중...")
                code = commandQueue.get().rstrip()
                # print(code)
                self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
                self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", command + "_req", command, 0,
                                        "0101")
            elif command == "opt90003\n":  # 프로그램매수상위순위요청 - 프로그램 매수상위 순위 15위까지 가져옴.
                # print("프로그램 매수상위 가져오는중...")
                while True:
                    if commandQueue.qsize() > 0:
                        break
                    else:
                        pass
                command = command.rstrip()
                # print(command)
                # print("시장구분정보 받아오는중...")
                sparam = commandQueue.get().rstrip()
                # print(sparam)
                global TypeInfomation

                if sparam == 'P00101':
                    TypeInfomation = '코스피'
                else:
                    TypeInfomation = '코스닥'

                self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "매매상위구분", "2")
                self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "금액수량구분", "2")  # 1 : 금액, 2 : 수량
                self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "시장구분", sparam)
                self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", command + "_req", command, 0,"0101")
            elif command == "opt10081\n":  # 주식일봉차트조회요청 - 기준일자(당일) 로부터 과거 600일 또는 그 이상을 가져옴. 우리는 60일.
                # print("차트 요청중...")
                while True:
                    if commandQueue.qsize() > 0:
                        break
                    else:
                        pass
                command = command.rstrip()
                print(command+"요청받았음")
                # print("종목코드 받아오는중...")
                code = commandQueue.get().rstrip()
                print(code+"요청받았음")

                # 기준날짜 문자열 생성을 위함.
                date = datetime.date.today()
                dateinfo = str(date.year) + str(date.month) + str(date.day)
                dateinfo = dateinfo.strip()
                # print(dateinfo)

                self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
                self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "기준일자", dateinfo)
                self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "0")
                self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", command + "_req", command, 0,"0101")

            elif command == "opt10059\n":  # 종목별투자기관별요청 - 각 투자자들의 순매수량을 알 수 있다.
                date = datetime.date.today()
                dateinfo = str(date.year) + str(date.month) + str(date.day)
                dateinfo = dateinfo.strip()
                # print(dateinfo)
                self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "일자", dateinfo)  # YYYYMMDD
                self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
                self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "금액수량구분", "2")  # 1 : 금액, 2 : 수량
                self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "매매구분", "0")  # 0 : 순매수, 1 : 매수, 2 : 매도
                self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "단위구분", "1")  # 0 : 천주, 1 : 단주
                self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", command + "_req", command, 0,
                                        "0101")
            else:
                pass
        else:
            pass

    def event_connect(self, err_code):
        if err_code == 0:
            print("키움증권 로그인 성공")

    def receive_trdata(self, screen_no, rqname, trcode, recordname, prev_next, data_len, err_code, msg1, msg2):
        if rqname == "opt10001_req":
            name = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, 0, "종목명")
            volume = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, 0, "거래량")

            name = name.strip()
            volume = volume.strip()

            print(name)
            print(volume)

            # Use For Dubugging
            # command = "종목명: " + name + "/거래량: " + volume + "\n"

        elif rqname == "opt90003_req":
            outjson = {}
            outjson['타입'] = '순위요청'
            outjson['시장구분'] = TypeInfomation
            # print('시장구분 : ' + TypeInfomation)
            contentlist = []
            for i in range(0, 15):
                rank = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "",
                                               rqname, i, "순위")
                code = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "",
                                               rqname, i, "종목코드")
                program_by_volume = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)",
                                                            trcode, "", rqname, i, "프로그램순매수금액")  # 실제로는 순매수수량이 출력됨.
                curr_money = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "",
                                                     rqname, i, "현재가")
                name = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "",
                                               rqname, i, "종목명")
                updown_icon = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode,
                                                      "", rqname, i, "등락기호")
                updown_rate = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode,
                                                      "", rqname, i, "등락율")

                rank = rank.strip()
                code = code.strip()
                program_by_volume = program_by_volume.strip()
                curr_money = curr_money.strip()
                name = name.strip()
                updown_icon = updown_icon.strip()
                updown_rate = updown_rate.strip()

                # Use For Dubugging
                # print(rank + '/' + name +  '/' + code + '/' + program_by_volume + '/' + curr_money + '/' + updown_icon + '/' + updown_rate + '\n')

        elif rqname == "opt10081_req":
            outjson = {}
            outjson['타입'] = '차트정보'
            contentlist = []
            for i in range(0, 60):
                curr_money = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "",
                                                     rqname, i, "현재가")
                start_money = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode,
                                                      "", rqname, i, "시가")
                high_money = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "",
                                                     rqname, i, "고가")
                low_money = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "",
                                                    rqname, i, "저가")
                date_info = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "",
                                                    rqname, i, "일자")

                curr_money = curr_money.strip()
                start_money = start_money.strip()
                high_money = high_money.strip()
                low_money = low_money.strip()
                date_info = date_info.strip()

                # Use For Dubugging
                # print('일자: ' + date_info + ' / 시가 : ' + start_money +  ' / 종가 : ' + curr_money + ' / 고가 : ' + high_money + ' / 저가 : ' + low_money + '\n')


        elif rqname == "opt10059_req":
            outjson = {}
            outjson['타입'] = '종목별투자기관정보'
            contentlist = []
            for i in range(0, 30):
                date_info = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "",
                                                    rqname, i, "일자").strip()
                curr_money = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "",
                                                     rqname, i, "현재가").strip()
                updown_icon = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode,
                                                      "", rqname, i, "대비기호").strip()
                indi_holder = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode,
                                                      "", rqname, i, "개인투자자").strip()
                forg_holder = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode,
                                                      "", rqname, i, "외국인투자자").strip()
                orga_holder = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode,
                                                      "", rqname, i, "기관계").strip()
                finance_holder = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode,
                                                      "", rqname, i, "금융투자").strip()
                insurance_holder = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "",
                                                    rqname, i, "보험").strip()
                tusin_holder = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "",
                                                rqname, i, "투신").strip()
                etcFinance_holder = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "",
                                                   rqname, i, "기타금융").strip()
                bank_holder = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "",
                                               rqname, i, "은행").strip()
                yeongi_holder = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "",
                                                rqname, i, "연기금등").strip()
                samofund_holder = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "",
                                               rqname, i, "사모펀드").strip()
                country_holder = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "",
                                               rqname, i, "국가").strip()
                etcLaw_holder = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "",
                                                 rqname, i, "기타법인").strip()
                naeforg_holder = self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "",
                                                  rqname, i, "내외국인").strip()

        else:
            pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    # myWindow.show()
    app.exec_()