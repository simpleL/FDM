# -*- coding:utf-8 -*- 

import sys
import getopt

from collector import *
from analyzer import *
from consts import *

def main(argv):
    c = Collector()
    c.collect_stock_information()
    c.collect_bonus()
    c.collect_daily(TUSHARE)

if __name__ == '__main__':
    main(sys.argv)