# -*- coding:utf-8 -*-

import datetime
import MySQLdb
import pandas
from utils import *

class Store:
    def get_all_stocks(self):
        conn = MySQLdb.connect("127.0.0.1", "root", "root", "quant", charset="utf8")
        sql_string = "select code from stock_information"
        cursor = conn.cursor()
        
        count = cursor.execute(sql_string)
        result = cursor.fetchall()
    
        codes = []
        for i in range(0, count):
            codes.append(result[i][0])
    
        cursor.close()
        conn.close()
    
        return codes

    def get_all_quotes(self):
        conn = MySQLdb.connect("127.0.0.1", "root", "root", "quant", charset="utf8")
        sql_string = "select * from market"
        cursor = conn.cursor()
        
        count = cursor.execute(sql_string)
        result = cursor.fetchall()
    
        cursor.close()
        conn.close()
        
        codes = []
        dates = []
        opens = []
        closes = []
        lows = []
        highs = []
        volumes = []
    
        for i in range(0, count):
            codes.append(result[i][1])
            dates.append(result[i][2])
            opens.append(result[i][3])
            closes.append(result[i][4])
            lows.append(result[i][5])
            highs.append(result[i][6])
            volumes.append(result[i][7])
    
        quotes = pandas.DataFrame({"code": codes, "date": dates, "open": opens, "close": closes,
                               "low": lows, "high": highs, "volume": volumes})
        return quotes
    
    def get_bonus(self, conn, code):
        sql_string = "select * from bonus where code = \"%s\""%(code)
        cursor = conn.cursor()
        
        count = cursor.execute(sql_string)
        result = cursor.fetchall()
        
        cursor.close()
        
        codes = []
        announce_dates = []
        stat_right_dates = []
        exright_dates = []
        dividends = []
        bonus_stocks = []
        tranadd_stocks = []
        
        for i in range(0, count):
            codes.append(result[i][1])
            announce_dates.append(result[i][2])
            stat_right_dates.append(result[i][3])
            exright_dates.append(result[i][4])
            dividends.append(result[i][5])
            bonus_stocks.append(result[i][6])
            tranadd_stocks.append(result[i][7])
        
        bonus = pandas.DataFrame({"code": codes, "announce_date": announce_dates,
                                  "stat_right_date": stat_right_dates, "exright_date": exright_dates,
                                  "dividend": dividends, "bonus_stock": bonus_stocks,
                                  "tranadd_stock": tranadd_stocks})
        
        return bonus

    def get_exright_quotes(self, conn, code):
        bonus = self.get_bonus(conn, code)
        bonus = bonus.set_index("exright_date")
        bonus = bonus.sort_index()
        bonus_index = 0
        if len(bonus) > 0 and bonus.index[0] == datetime.datetime.strptime("1900-01-01", "%Y-%m-%d").date():
            bonus_index = 1
        query_bonus_sql = "select * from market where code = '%s' order by date asc"%(code)

        cursor = conn.cursor()
        
        count = cursor.execute(query_bonus_sql)
        result = cursor.fetchall()
        
        cursor.close()
    
        codes = []
        dates = []
        opens = []
        closes = []
        lows = []
        highs = []
        volumes = []
        last_closes = []
        factors = []
    
        last_close = 0
        factor = 1
        for i in range(0, count):
            date = result[i][2]
            exright_price = last_close
            if bonus_index < len(bonus) and date >= bonus.index[bonus_index]:
                if last_close > 0:
                    exright_info = exright(bonus.iloc[bonus_index], last_close)
                    last_close = exright_info["price"]
                    factor = factor * exright_info["factor"]
                else:
                    print "code is %s, date is %s"%(code, bonus.index[bonus_index].strftime("%Y-%m-%d"))
                bonus_index = bonus_index + 1
            
                codes.append(result[i][1])
                dates.append(date)
                opens.append(result[i][3])
                closes.append(result[i][4])
                lows.append(result[i][5])
                highs.append(result[i][6])
                volumes.append(result[i][7])
                last_closes.append(last_close)
                factors.append(factor)
            
                last_close = result[i][4]
    
        quotes = pandas.DataFrame({"code": codes, "date": dates, "open": opens, "close": closes,
                                   "low": lows, "high": highs, "volume": volumes,
                                   "last_close": last_closes, "factor": factors})

        quotes = quotes.set_index("date")
        quotes = quotes.sort_index()
    
        return quotes

