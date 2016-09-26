# -*- coding:utf-8 -*- 

import datetime
import threading
import tushare
import MySQLdb
import pandas

from .utils import StringUtils
from conn_manager import ConnManager
from consts import *
from store import Store
import crawler

def _collect_internal(collector, start_date, end_date, codes, source):
    conn = ConnManager.get_conn()

    for code in codes:
        collector.collect_trades(conn, code, start_date, end_date, source)

class Collector:
    def __init__(self):
        self.store = Store();
        self.xueqiu = crawler.CrawlerForXueqiu()
        self._10jqka = crawler.CrawlerFor10JQKA()

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
        stocks = pandas.DataFrame()
        try:
            stocks = tushare.get_stock_basics()
        except:
            print "collect stock information error"
            return
    
        conn = ConnManager.get_conn()
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
    
    def collect_bonus(self):
        codes = self.store.get_all_stocks()
    
        conn = ConnManager.get_conn()
        cursor = conn.cursor()
    
        insert_sql = "insert into bonus (code, announce_date, stat_right_date, exright_date, dividend, bonus_stock, tranadd_stock) values (%s, %s, %s, %s, %s, %s, %s)"
    
        for code in codes:
            server_stock_bonus = crawler.get_dividend(code)
            if len(server_stock_bonus) > 0:
                server_stock_bonus = server_stock_bonus.set_index("announce_date")
                server_stock_bonus = server_stock_bonus.sort_index()
        
            stock_bonus = self.store.get_bonus(code)
            if len(stock_bonus) > 0:
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

    def collect_finance(self):
        codes = self.store.get_all_stocks()
    
        ConnManager.get_conn()
        cursor = conn.cursor()
        print "collect finance"
        
        insert_sql = "insert into finance (code, date, earning_per_share, net_margin, nonrecurring_net_margin,"\
                     "total_income, asset_per_share, roe, diluted_roe, debt_ratio, fund_per_share,"\
                     "undistributed_profit_per_share, cash_flow_per_share) values"\
                     "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
    
        for code in codes:
            server_stock_finance = self._10jqka.get_finance_data(code)
            if len(server_stock_finance) > 0:
                server_stock_finance = server_stock_finance.set_index("date")
                server_stock_finance = server_stock_finance.sort_index()
        
            stock_finance = self.store.get_finance(code)
            if len(stock_finance) > 0:
                stock_finance = stock_bonus.set_index("date")
                stock_finance = stock_bonus.sort_index()
        
            diff = server_stock_finance.index.difference(stock_finance.index)
        
            insert_list = []
        
            for date in diff:
                finance = server_stock_finance.loc[date]
                params = (finance.code, date, finance.earning_per_share, finance.net_margin,
                          finance.nonrecurring_net_margin, finance.total_income, finance.asset_per_share,
                          finance.roe, finance.diluted_roe, finance.debt_ratio, finance.fund_per_share,
                          finance.undistributed_profit_per_share, finance.cash_flow_per_share)
                insert_list.append(params)
        
            if len(insert_list) > 0:
                cursor.executemany(insert_sql, insert_list)
                conn.commit()
        
        cursor.close()