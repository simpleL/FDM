# -*- coding: utf-8 -*-
from .crawler import CrawlerForXueqiu
from . import DBInitializer

if __name__ == "__main__":
    d = DBInitializer()
    d.start()
    #c = CrawlerForXueqiu()
    #print c.get_h_data("002174", "1989-01-01", "2016-09-11")