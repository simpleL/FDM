# -*- coding: utf-8 -*-
import datetime
import math
import time
import tushare

from conn_manager import ConnManager
from store import Store
from ui import UITool
from utils import CalcUtils

class RealTimeAnalyzer:
    kUpdateInterval = 5

    kBeforeMorningCall = 0
    kMorningCallCancelable = 1
    kMorningCallUncancelable = 2
    kAfterMorningCall = 3
    kMorningTrade = 4
    kNoonClose = 5
    kAfternoonTrade = 6
    kAfternoonCall = 7
    kAfternoonClose = 8

    def __init__(self):
        self.__tracking_codes = ["002174"]
        self.__ui_tool = UITool()
        temp = datetime.datetime.now()
        self.morningCallStartTime = datetime.datetime(temp.year, temp.month, temp.day, 9, 15, 0)
        self.morningCallCancelableTime = datetime.datetime(temp.year, temp.month, temp.day, 9, 20, 0)
        self.morningCallEndTime = datetime.datetime(temp.year, temp.month, temp.day, 9, 25, 0)
        self.morningTradeStartTime = datetime.datetime(temp.year, temp.month, temp.day, 9, 30, 0)
        self.morningTradeEndTime = datetime.datetime(temp.year, temp.month, temp.day, 11, 30, 0)
        self.afternoonTradeStartTime = datetime.datetime(temp.year, temp.month, temp.day, 13, 0, 0)
        self.afternoonCallStartTime = datetime.datetime(temp.year, temp.month, temp.day, 14, 57, 0)
        self.afternoonTradeEndTime = datetime.datetime(temp.year, temp.month, temp.day, 15, 0, 0)
        self.__init_codes()

    def __init_codes(self):
        self.__code_data = {}
        conn = ConnManager.get_conn()
        cursor = conn.cursor()
        codes_to_remove = []

        cu = CalcUtils()
        s = Store()
        today = datetime.datetime.now().date()

        for code in self.__tracking_codes:
            info = {}

            sql = "select date, close from market where code = '%s' order by date desc limit 1"%(code)
            cursor = conn.cursor()
            cursor.execute(sql)
            result = cursor.fetchall()

            if len(result) < 1:
                codes_to_remove.append(code)
                continue

            prev_day = result[0][0]
            last_close = result[0][1]

            bonus = s.get_bonus(code)
            if len(bonus) > 0:
                bonus = bonus.set_index("exright_date")
                bonus = bonus.sort_index()
                idx = len(bonus) - 1
                bonus_date = bonus.index[idx]

                if bonus_date == today or (today > bonus_date and prev_day < bonus_date):
                    last_close = cu.exright(bonus.iloc[idx], last_close)["price"]

            info["last_close"] = float(last_close)

            print "last close of %s is %.2f"%(code, last_close)

            self.__code_data[code] = info

        for code in codes_to_remove:
            print "remove new stock %s"%s(code)
            self.__tracking_codes.remove(code)

    def __minus_to_seconds(self, time1, time2):
        return math.ceil((time1 - time2).total_seconds())

    def __get_period_for_time(self, time):
        if time < self.morningCallStartTime:
            return (RealTimeAnalyzer.kBeforeMorningCall, self.__minus_to_seconds(self.morningCallStartTime, time))
        elif time < self.morningCallCancelableTime:
            return (RealTimeAnalyzer.kMorningCallCancelable, 30)
        elif time < self.morningCallEndTime:
            return (RealTimeAnalyzer.kMorningCallUncancelable, RealTimeAnalyzer.kUpdateInterval)
        elif time < self.morningTradeStartTime:
            return (RealTimeAnalyzer.kAfterMorningCall, self.__minus_to_seconds(self.morningTradeStartTime, time))
        elif time < self.morningTradeEndTime:
            return (RealTimeAnalyzer.kMorningTrade, RealTimeAnalyzer.kUpdateInterval)
        elif time < self.afternoonTradeStartTime:
            return (RealTimeAnalyzer.kNoonClose, self.__minus_to_seconds(self.afternoonTradeStartTime, time))
        elif time < self.afternoonCallStartTime:
            return (RealTimeAnalyzer.kAfternoonTrade, RealTimeAnalyzer.kUpdateInterval)
        elif time < self.afternoonTradeEndTime:
            return (RealTimeAnalyzer.kAfternoonCall, RealTimeAnalyzer.kUpdateInterval)
        else:
            return (RealTimeAnalyzer.kAfternoonClose, 0)

    def __print_quotes(self, q, callTime):
        if callTime:
            print "\tprice\tamount\na1\t%.2f\t%d\nb1\t%.2f\t%d\n"%(q.a1_p, q.a1_v, q.b1_p, q.b1_v)
        else:
            print "\tprice\tamount\nprice\t%.2f\na5\t%.2f\t%d\na4\t%.2f\t%d\na3\t%.2f\t%d\na2\t%.2f\t%d\na1\t%.2f\t%d\n"\
                  "\nb1\t%.2f\t%d\nb2\t%.2f\t%d\nb3\t%.2f\t%d\nb4\t%.2f\t%d\nb5\t%.2f\t%d\n"%(
                        q.price, q.a5_p, q.a5_v, q.a4_p, q.a4_v, q.a3_p, q.a3_v, q.a2_p, q.a2_v, q.a1_p, q.a1_v,
                        q.b1_p, q.b1_v, q.b2_p, q.b2_v, q.b3_p, q.b3_v, q.b4_p, q.b4_v, q.b5_p, q.b5_v)

    def __process_code(self, code, callTime):
        q = tushare.get_realtime_quotes(code)

        try:
            self.__print_quotes(q, callTime)
        except:
            print "error data, will retry later..."
            return

        info = self.__code_data[code]
        last_close = info["last_close"]
        changepercent = (float(q.price) - last_close) / last_close * 100
        stage = math.floor(math.fabs(changepercent / 0.5))
        if changepercent < 0:
            stage = - stage

        last_stage = 0
        if info.has_key("last_stage"):
            last_stage = info["last_stage"]

        if last_stage != stage:
            info["last_stage"] = stage
            self.__ui_tool.notify("change notice", "%s changepercent is %.2f%%, and price is %.2f"%(code, changepercent, q.price))


    def __process(self, time, period):
        if period == RealTimeAnalyzer.kBeforeMorningCall:
            print "waiting for call..."
            return

        if period == RealTimeAnalyzer.kAfterMorningCall:
            print "waiting for open market..."
            return

        if period == RealTimeAnalyzer.kNoonClose:
            print "waiting for afternoon open..."
            return

        print time
        for code in self.__tracking_codes:
            szCode = code[0] != '6'
            callTime = period == RealTimeAnalyzer.kMorningCallUncancelable or\
                       period == RealTimeAnalyzer.kMorningCallCancelable or\
                       (period == RealTimeAnalyzer.kAfterMorningCall and szCode)
            self.__process_code(code, callTime)


    def run(self):
        print "run"
        while True:
            now = datetime.datetime.now()
            period, interval = self.__get_period_for_time(now)
            if period == RealTimeAnalyzer.kAfternoonClose:
                print "stop on market close..."
                break
            else:
                self.__process(now, period)
                time.sleep(interval)
