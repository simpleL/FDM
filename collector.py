# -*- coding:utf-8 -*- 

import datetime
import threading
import tushare
import MySQLdb

from .utils import StringUtils
from consts import *
from store import Store
import crawler

def _collect_internal(collector, start_date, end_date, codes, source):
    conn = MySQLdb.connect("127.0.0.1", "root", "root", "quant")

    for code in codes:
        collector.collect_trades(conn, code, start_date, end_date, source)
    
    conn.close()

class Collector:
    def __init__(self):
        self.store = Store();
        self.xueqiu = crawler.CrawlerForXueqiu()

    def collect_trades(self, conn, code, start, end, source):
        sql_string = "insert into market (code, date, open, close, low, high, volume) values (%s, %s, %s, %s, %s, %s, %s)"

        stock_data = None;
        if source == SOHU:
            stock_data = crawler.get_h_data(code, start, end)
        elif source == XUEQIU:
            stock_data = self.xueqiu.get_h_data(code, start, end)
        elif source == TUSHARE:
            stock_data = tushare.get_hist_data(code, start = start, end = end)
        
        if (stock_data is None):
            print "%s has no data"%(code)
        else:
            cursor = conn.cursor()
            list = [];
            for i in range(0, stock_data.count().open):
                param = (code, stock_data.index[i],
                         stock_data.open[i], stock_data.close[i],
                         stock_data.low[i], stock_data.high[i],
                         stock_data.volume[i])
                list.append(param)
            cursor.executemany(sql_string, list)
            conn.commit()
            cursor.close()

    def collect(self, start_date, source):
        date = datetime.datetime.now();
        date_string = date.strftime("%Y-%m-%d")
        codes = self.store.get_all_stocks()

        MAX_THREADS = 10
        codes_num = len(codes)
        codes_per_thread = codes_num / MAX_THREADS
        # 这里应该多线程
        for i in range(0, MAX_THREADS):
            start = i * codes_per_thread
            end = start + codes_per_thread
            if i == MAX_THREADS - 1:
                end = codes_num
            t = threading.Thread(target=_collect_internal, args = (self, start_date, date_string, codes[start:end], source))
            t.start()
            t.join()
    

    def collect_market(self, source):
        self.collect("1989-01-01", source)
	
    def collect_daily(self, source):
        date = datetime.datetime.now();
        date_string = date.strftime("%Y-%m-%d")
        self.collect(date_string, source)

    def collect_stock_information(self):
        stocks = tushare.get_stock_basics();
    
        conn = MySQLdb.connect("127.0.0.1", "root", "root", "quant", charset="utf8")
        cursor = conn.cursor()
        update_list = [];
        insert_list = [];
    
        su = StringUtils()
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
                param = (su.get_string(stock["name"]), su.get_string(stock.industry),
                         su.get_string(stock.area), stock.outstanding * 10000,
                         stock.totals * 10000, stock.pe, stock.pb, code)
                #print param
                update_list.append(param)
            else:
                param = (code, su.get_string(stock["name"]),
                         su.get_string(stock.industry), su.get_string(stock.area),
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
    
    def collect_bonus(self):
        codes = self.store.get_all_stocks()
    
        conn = MySQLdb.connect("127.0.0.1", "root", "root", "quant", charset="utf8")
        cursor = conn.cursor()
    
        insert_sql = "insert into bonus (code, announce_date, stat_right_date, exright_date, dividend, bonus_stock, tranadd_stock) values (%s, %s, %s, %s, %s, %s, %s)"
    
        for code in codes:
            server_stock_bonus = crawler.get_dividend(code)
            server_stock_bonus = server_stock_bonus.set_index("announce_date")
            server_stock_bonus = server_stock_bonus.sort_index()
        
            stock_bonus = self.store.get_bonus(conn, code)
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

    def collect_finance(self):
        codes = self.store.get_all_stocks()
    
        conn = MySQLdb.connect("127.0.0.1", "root", "root", "quant", charset="utf8")
        cursor = conn.cursor()
        print "collect finance"
        '''
        insert_sql = "insert into bonus (code, announce_date, stat_right_date, exright_date, dividend, bonus_stock, tranadd_stock) values (%s, %s, %s, %s, %s, %s, %s)"
    
        for code in codes:
            server_stock_bonus = get_dividend(code)
            server_stock_bonus = server_stock_bonus.set_index("announce_date")
            server_stock_bonus = server_stock_bonus.sort_index()
        
            stock_bonus = self.store.get_bonus(conn, code)
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
        '''
        cursor.close()
        conn.close()