# -*- coding: utf-8 -*-
from .crawler import CrawlerForXueqiu
from . import DBInitializer

if __name__ == "__main__":
    d = DBInitializer()
    d.start()