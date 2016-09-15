# -*- coding:utf-8 -*- 

import sys
import getopt
import datetime

from collector import *
from analyzer import *
from consts import *
from pref_service import PrefService

def main(argv):
    c = Collector()
    prefs = PrefService()
    now = datetime.datetime.now().date()
    now_string = now.strftime("%Y-%m-%d")
    last_date_string = prefs.get_value("daily_collect_task_date")
    if not last_date_string or last_date_string != now_string:
        print "do daily collect task"
        c.collect_stock_information()
        c.collect_daily(TUSHARE)
        prefs.set_value("daily_collect_task_date", now_string)
    
    bonus_date_string = prefs.get_value("bonus_collect_date")
    if not bonus_date_string:
        c.collect_bonus()
        print "collect bonus"
        prefs.set_value("bonus_collect_date", now_string)
    else:
        bonus_date = datetime.datetime.strptime(bonus_date_string, "%Y-%m-%d").date()
        minus = now - bonus_date
        if minus.days >= 3:
            '''
            we don't need to collect bonus data every day,
            since it will not change so often
            '''
            c.collect_bonus()
            print "collect bonus"
            prefs.set_value("bonus_collect_date", now_string)
    
if __name__ == '__main__':
    main(sys.argv)