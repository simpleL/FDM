# -*- coding:utf-8 -*- 

import datetime
import threading
import tushare
import MySQLdb

from store import *
from utils import *
from crawler.dividend import *
from crawler.market import *

def collect_trades(conn, code, start, end):
    sql_string = "insert into market (code, date, open, close, low, high, volume, amount) values (%s, %s, %s, %s, %s, %s, %s, %s)"

    stock_data = get_h_data(code, start, end);
    if (stock_data is None):
        print code
    else:
        cursor = conn.cursor()
        list = [];
        for i in range(0, stock_data.count().open):
            param = (code, stock_data.index[i],
                     stock_data.open[i], stock_data.close[i],
                     stock_data.low[i], stock_data.high[i],
                     stock_data.volume[i], stock_data.amount[i])
            list.append(param)
        cursor.executemany(sql_string, list)
        conn.commit()
        cursor.close()
        
def collect_internal(start_date, end_date, codes):
    conn = MySQLdb.connect("127.0.0.1", "root", "root", "quant")
    
    for code in codes:
       collect_trades(conn, code, start_date, end_date)
    
    conn.close()

def collect(start_date):
    date = datetime.datetime.now();
    date_string = date.strftime("%Y-%m-%d")
    codes = get_all_stocks()

    MAX_THREADS = 10
    codes_num = len(codes)
    codes_per_thread = codes_num / MAX_THREADS
    # 这里应该多线程
    for i in range(0, MAX_THREADS):
        start = i * codes_per_thread
        end = start + codes_per_thread
        if i == MAX_THREADS - 1:
            end = codes_num
        t = threading.Thread(target=collect_internal, args = (start_date, date_string, codes[start:end]))
        t.start()
        t.join()
    

def collect_market():
    collect("1989-01-01")
	
def collect_daily():
    date = datetime.datetime.now();
    date_string = date.strftime("%Y-%m-%d")
    collect(date_string)

def collect_stock_information():
    stocks = tushare.get_stock_basics();
    
    conn = MySQLdb.connect("127.0.0.1", "root", "root", "quant", charset="utf8")
    cursor = conn.cursor()
    update_list = [];
    insert_list = [];
    
    for code in stocks.index:
        stock = stocks.loc[code]
        query_sql = "select * from stock_information where code = '" + code + "'"
        
        update_sql = "update stock_information s " +\
                     "set s.name = %s," +\
                     "s.industry = %s," +\
                     "s.area = %s," +\
                     "s.floating = %s," +\
                     "s.total = %s," +\
                     "s.pe = %s," +\
                     "s.pb = %s" +\
                     "where s.code = %s"
        insert_sql = "insert into stock_information (code, name, industry, area, floating, total, pe, pb) " +\
                     "values (%s, %s, %s, %s, %s, %s, %s, %s)"
        count = cursor.execute(query_sql)
        if (count > 0):
            param = (get_string(stock["name"]), get_string(stock.industry),
                     get_string(stock.area), stock.outstanding * 10000,
                     stock.totals * 10000, stock.pe, stock.pb, code)
            #print param
            update_list.append(param)
        else:
            param = (code, get_string(stock["name"]),
                     get_string(stock.industry), get_string(stock.area),
                     stock.outstanding * 10000, stock.totals * 10000, stock.pe, stock.pb)
            insert_list.append(param)
    
    if (len(insert_list) != 0):
        cursor.executemany(insert_sql, insert_list)
        conn.commit()
    if (len(update_list) != 0):
        cursor.executemany(update_sql, update_list)
        conn.commit()
    
    cursor.close()
    conn.close()
    
def collect_bonus():
    codes = get_all_stocks()
    
    conn = MySQLdb.connect("127.0.0.1", "root", "root", "quant", charset="utf8")
    cursor = conn.cursor()
    
    insert_sql = "insert into bonus (code, announce_date, stat_right_date, exright_date, dividend, bonus_stock, tranadd_stock) values (%s, %s, %s, %s, %s, %s, %s)"
    
    for code in codes:
        server_stock_bonus = get_dividend(code)
        server_stock_bonus = server_stock_bonus.set_index("announce_date")
        server_stock_bonus = server_stock_bonus.sort_index()
        
        stock_bonus = get_bonus(conn, code)
        stock_bonus = stock_bonus.set_index("announce_date")
        stock_bonus = stock_bonus.sort_index()
        
        diff = server_stock_bonus.index.difference(stock_bonus.index)
        
        insert_list = []
        
        for announce_date in diff:
            bonus = server_stock_bonus.loc[announce_date]
            params = (bonus.code, announce_date, bonus.stat_right_date,
                      bonus.exright_date, bonus.dividend, bonus.bonus_stock,
                      bonus.tranadd_stock)
            insert_list.append(params)
        
        if len(insert_list) > 0:
            cursor.executemany(insert_sql, insert_list)
            conn.commit()
        
    cursor.close()
    conn.close()