# -*- coding:utf-8 -*- 

import datetime
import MySQLdb
import pandas
import math
import time

from consts import *
from store import *
from utils import CalcUtils

def stat_surge_limit(trades):
    result = {}
    
    last_date = 0
    cu = CalcUtils()
    for i in range(1, len(trades))[::-1]:
        trade = trades.iloc[i]
        type = cu.get_change_type(trade)
        if type == YIZI_ZT or type == ZT:
            last_date = last_date + 1
        else:
            if last_date > 0:
                result["last_date"] = last_date
                result["code"] = str(trade.code)
                result["start_date"] = trades.index[i + 1].strftime("%Y-%m-%d")
            break

    return result

def stat_constant_rise(trades):
    result = {}

    last_date = 0
    last_type = -1
    cu = CalcUtils()
    for i in range(1, len(trades))[::-1]:
        trade = trades.iloc[i]
        type = cu.get_change_type(trade)
        if type == YIZI_ZT or type == ZT or type == ZT_FAIL or type == RISE:
            last_date = last_date + 1
        else:
            if last_date > 0:
                if not (last_type == RISE and last_date == 1):
                    prev = trades.iloc[i]
                    now = trades.iloc[len(trades) - 1]
                    result["last_date"] = last_date
                    result["code"] = str(trade.code)
                    result["start_date"] = trades.index[i + 1].strftime("%Y-%m-%d")

                    result["change_percent"] = float("%.2f"%(float(now.close - prev.close) / float(prev.close) * 100))
            break

        last_type = type

    return result

# 横盘，向上突破迹象
def stat_narrowly_range(trades):
    result = {}
    
    # 相邻两天的波动范围
    kRangeLimit = 3;
    # 一定天数的波动
    kDaysInterval = 5;
    # 一定天数的波动范围
    kDaysRangeLimit = 10;
    
    last_days = 0
    for i in range(0, len(trades)):
        trade = trades.iloc[i];
        early_trade = trades.iloc[i - last_days];
        
        last_close = trade.last_close;
        if (last_close < 0.01):
            print "%s last close is %f"%(trade.code, float(trade.last_close))
            last_close = trade.open;
        today_range = (float(trade.close) - float(last_close)) * 100.0 / float(last_close);
        days_range = (float(trade.close) - float(early_trade.close)) * 100.0 / float(early_trade.close);
        
        if abs(today_range) < kRangeLimit or abs(days_range) < kDaysRangeLimit:
            last_days = last_days + 1;
        else:
            if last_days > kDaysInterval and (days_range > 0 or today_range > 0):
                # 向上突破迹象
                result["code"] = trade.code;
                # 日期已经变成了索引，所以需要用name来访问
                result["date"] = trade.name;
                result["today_change"] = today_range;
                result["days_change"] = days_range;
                break;
            last_days = 0;
    
    return result

# 股价偏离初始值，前期手动添加，希望后期能够自动化处理
def stat_bias_alarm():
    result = {}
    
    return result

def daily_report():
    conn = MySQLdb.connect("127.0.0.1", "root", "root", "quant", charset="utf8")
    s = Store()
    codes = s.get_all_stocks()
    
    start_time = time.time() - 86400 * 60
    start_date = datetime.datetime.fromtimestamp(start_time).date()
    
    surges = pandas.DataFrame()
    rises = pandas.DataFrame()
    narrowly_ranges = pandas.DataFrame()
    
    for code in codes:
        # 除权后价格
        trades = s.get_exright_quotes(conn, code)
        if len(trades) == 0:
            continue
        trades = trades.query("date > @start_date")
        
        surge = stat_surge_limit(trades)
        if len(surge) > 0:
            surges = surges.append(surge, ignore_index = True)
        
        rise = stat_constant_rise(trades)
        if len(rise) > 0:
            rises = rises.append(rise, ignore_index = True)
        
        narrowly_range = stat_narrowly_range(trades)
        if len(narrowly_range) > 0:
            narrowly_ranges = narrowly_ranges.append(narrowly_range, ignore_index = True)
        
    conn.close()
    
    return narrowly_ranges

if __name__ == '__main__':
    conn = MySQLdb.connect("127.0.0.1", "root", "root", "quant", charset="utf8")
    """
    trades = get_exright_quotes(conn, "002388")
    start_time = time.time() - 86400 * 50
    start_date = datetime.datetime.fromtimestamp(start_time).date()
    trades = trades.query("date > @start_date")
    print stat_constant_rise(trades)
    """
    result = daily_report().sort_values(by="last_date")
    #result = daily_report().sort_values(by="change_percent")
    print result
