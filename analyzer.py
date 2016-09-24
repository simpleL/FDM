# -*- coding:utf-8 -*- 

import datetime
import MySQLdb
import pandas
import math
import os

from consts import *
from store import Store
from utils import CalcUtils
    
"""
    �����ǵ�ͣ��
Parameters
------
    stock_quotes: DataFrame
return
------
DataFrame

"""
def analyze_extreme_changes(result, stock_quotes, types):
    cu = CalcUtils()
    last_close = stock_quotes.close[0];
    
    if (len(stock_quotes.index) == 1):
        return result
    
    last_date = 0
    dict = {}
    for i in range(1, len(stock_quotes.index)):
        trade = stock_quotes.iloc[i]
        
        change_type = cu.get_change_type(trade)
        
        matches = False
        for type in types:
            if change_type == type:
                matches = True
                break
                
        if matches:
            # ���㲨������
            if (last_date == 0):
                dict["start_date"] = stock_quotes.index[i].strftime("%Y-%m-%d")
                dict["code"] = stock_quotes.code[i]
            last_date = last_date + 1
        else:
            # ��������/�µ���ֹ
            if (len(dict) > 0):
                #print trade
                dict["end_date"] = stock_quotes.index[i].strftime("%Y-%m-%d")
                dict["last_date"] = last_date
                last_fq_close = float(stock_quotes.close[i - 1]) / stock_quotes.factor[i - 1]
                dict["one_day_change"] = (float(stock_quotes.close[i]) / stock_quotes.factor[i] - last_fq_close) / last_fq_close
                if (i + 2 < len(stock_quotes.index)):
                    dict["three_day_change"] = (float(stock_quotes.close[i + 2]) / stock_quotes.factor[i + 2] - last_fq_close) / last_fq_close
                else:
                    dict["three_day_change"] = 0;
                if (i + 4 < len(stock_quotes.index)):
                    dict["five_day_change"] = (float(stock_quotes.close[i + 4]) / stock_quotes.factor[i + 4] - last_fq_close) / last_fq_close
                else:
                    dict["five_day_change"] = 0;
                if (i + 9 < len(stock_quotes.index)):
                    dict["ten_day_change"] = (float(stock_quotes.close[i + 9]) / stock_quotes.factor[i + 9] - last_fq_close) / last_fq_close
                else:
                    dict["ten_day_change"] = 0;
                if (i + 19 < len(stock_quotes.index)):
                    dict["twenty_day_change"] = (float(stock_quotes.close[i + 19]) / stock_quotes.factor[i + 19] - last_fq_close) / last_fq_close
                else:
                    dict["twenty_day_change"] = 0;
                result = result.append(dict, ignore_index=True)
                
                dict = {}
                last_date = 0
    
    if (len(dict) > 0):
        dict["end_date"] = "NaN"
        dict["last_date"] = last_date
        dict["one_day_change"] = 0
        dict["three_day_change"] = 0
        dict["five_day_change"] = 0
        dict["ten_day_change"] = 0
        dict["twenty_day_change"] = 0
        result = result.append(dict, ignore_index=True)
    
    return result

def analyze_bonus():
    conn = MySQLdb.connect("127.0.0.1", "root", "root", "quant", charset="utf8")
    s = Store()
    codes = s.get_all_stocks()
    arr = []
    for code in codes:
        print "analyzing %s..."%(code)
        bonus = s.get_bonus(conn, code)
        if len(bonus) > 0:
            bonus = bonus.set_index("announce_date")
            bonus = bonus.sort_index()
        else:
            continue
        finance = s.get_finance(conn, code)
        if len(finance) > 0:
            finance = finance.set_index("date")
            finance = finance.sort_index()
        
        sql = "select MIN(date) from market where code = \"%s\""%(code)
        cursor = conn.cursor()
        count = cursor.execute(sql)
        if count == 0:
            continue
        start_date = cursor.fetchone()[0]
        cursor.close()
        bonus_index = 0
        for i in range(0, len(finance)):
            if bonus_index >= len(bonus):
                break;
            
            bonus_date = bonus.index[bonus_index]
            date = finance.index[i]
            if date < start_date:
                continue
            next_date = datetime.date(2199, 12, 31)
            if i < len(finance) - 1:
                next_date = finance.index[i + 1]
            
            if bonus_date > date and bonus_date <= next_date:
                f = finance.iloc[i]
                b = bonus.iloc[bonus_index]
                dict = {}
                dict["date"] = date
                dict["announce_date"] = bonus_date
                dict["code"] = f.code
                dict["fund"] = f.fund_per_share
                dict["total"] = b.bonus_stock + b.tranadd_stock
                dict["exright_date"] = b.exright_date
                arr.append(dict)
                bonus_index = bonus_index + 1
    
    conn.close()
    return pandas.DataFrame(arr)

def analyze():
    conn = MySQLdb.connect("127.0.0.1", "root", "root", "quant", charset="utf8")
    s = Store()
    codes = s.get_all_stocks()
    
    result = pandas.DataFrame({"code": [], "start_date": [], "end_date": [], "last_date": [],
                               "one_day_change": [], "three_day_change": [], "five_day_change": [],
                               "ten_day_change":[], "twenty_day_change": []})
    
    for code in codes:
        stock_quotes = s.get_exright_quotes(conn, code)
        """
        �¹�
        """
        if (len(stock_quotes) == 0):
            print code
            continue
        
        result = analyze_extreme_changes(result, stock_quotes, [YIZI_ZT])

    conn.close()
    
    return result

if __name__ == '__main__':
    result = analyze_bonus()
    path = "%s/FDM Data/analyze_bonus.csv"%(os.getcwd())
    print result
    result.to_csv(path)