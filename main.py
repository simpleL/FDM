# -*- coding:utf-8 -*- 

import sys
import getopt

from collector import *
from analyzer import *

def main(argv):
    try:
        opts, args = getopt.getopt(argv[1:], 'hvo:', ['act='])
    except getopt.GetoptError, err:
        print str(err)
        sys.exit(2)
    for o, a in opts:
        if o in ('--act'):
            if (a == "market"):
                collect_market()
            elif (a == "daily"):
                collect_daily()
            elif (a == "stocks"):
                collect_stock_information()
            elif (a == "analyze"):
                analyze()
            elif (a == "bonus"):
                collect_bonus()

if __name__ == '__main__':
    main(sys.argv)