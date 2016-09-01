# -*- coding: utf-8 -*-
from .crawler import CrawlerForXueqiu
from . import DBInitializer

if __name__ == "__main__":
    d = DBInitializer()
    d.start()
    #c = CrawlerForXueqiu()
    #print c.get_hist_data("002174", use_cache=False)