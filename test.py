# -*- coding: utf-8 -*-
import crawler
from . import DBInitializer
from analyzer import *
from consts import *
from store import Store
from collector import Collector
from pref_service import PrefService
import MySQLdb
import os
import tushare

if __name__ == "__main__":
    d = DBInitializer()
    d.start()
    #c = crawler.CrawlerForXueqiu()
    #print c.get_h_data("002174", "1989-01-01", "2016-09-11")
    #codes = s.get_all_stocks()
    #empty = []
    #conn = MySQLdb.connect("127.0.0.1", "root", "root", "quant")
    #s = Store()
    #bonus = s.get_bonus(conn, "002174")
    #print bonus
    #for code in codes:
    #    trades = s.get_exright_quotes(conn, code)
    #    if len(trades) == 0:
    #        empty.append(code)
    #        print code
    #
    #print empty
    #codes = []

    #c = Collector()
    #for code in codes:
    #    c.collect_trades(conn, code, "2016-09-13", "2016-09-14", TUSHARE)
    #result = analyze()
    #path = "%s/FDM Data/analyze0.csv"%(os.getcwd())
    #print path
    #result.to_csv(path)
    
    #c = crawler.CrawlerFor10JQKA()
    #print c.get_finance_data("002174")