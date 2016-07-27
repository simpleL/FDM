# -*- coding: utf-8 -*-
from .crawler import CrawlerForXueqiu
from . import DBInitializer

if __name__ == "__main__":
    e = DBInitializer()
    d = DBInitializer()
    d.start()
    print CrawlerForXueqiu
    c = CrawlerForXueqiu()
    c.get_hist_data("600000")
    c.get_hist_data("002174")
    #c.get_hist_data("600000")