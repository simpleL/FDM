# -*- coding: utf-8 -*-
from .crawler import CrawlerForXueqiu
from . import DBInitializer
from consts import *
from store import Store
from collector import Collector
import MySQLdb

if __name__ == "__main__":
    #d = DBInitializer()
    #d.start()
    #c = CrawlerForXueqiu()
    #print c.get_h_data("002174", "1989-01-01", "2016-09-11")
    #s = Store()
    #codes = s.get_all_stocks()
    #empty = []
    conn = MySQLdb.connect("127.0.0.1", "root", "root", "quant")
    #for code in codes:
    #    trades = s.get_exright_quotes(conn, code)
    #    if len(trades) == 0:
    #        empty.append(code)
    #        print code
    #
    #print empty
    codes = ['603189', '603067', '601500', '601128', '600908', '600732', '600710', '300542',
             '300541', '300536', '300534', '300372', '002812', '000155', '000033', '603887']

    c = Collector()
    for code in codes:
        c.collect_trades(conn, code, "1989-01-01", "2016-09-13", XUEQIU)
