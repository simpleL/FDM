# -*- coding: utf-8 -*-
from .crawler import CrawlerForXueqiu
from . import DBInitializer
from store import Store
import MySQLdb

if __name__ == "__main__":
    #d = DBInitializer()
    #d.start()
    #c = CrawlerForXueqiu()
    #print c.get_h_data("002174", "1989-01-01", "2016-09-11")
    s = Store()
    codes = s.get_all_stocks()
    empty = []
    conn = MySQLdb.connect("127.0.0.1", "root", "root", "quant")
    for code in codes:
        trades = s.get_exright_quotes(conn, code)
        if len(trades) == 0:
            empty.append(code)
    
    print empty