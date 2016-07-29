# -*- coding: utf-8 -*-

import ConfigParser
import datetime
import json
import os
import pandas
import requests
import time

from ..utils import DateHelper

class CrawlerForXueqiu:
    def __init__(self):
        conf_path = "%s/FDM/crawler/xueqiu.conf"%(os.getcwd())
        self.__conf = ConfigParser.ConfigParser()
        self.__conf.read(conf_path)
        self.__hist_url = self.__conf.get("xueqiu", "hist_url")
        cache_dir = self.__conf.get("xueqiu", "cache_dir")
        self.__cache_dir = "%s/%s"%(os.getcwd(), cache_dir)
        
        user_agent = self.__conf.get("xueqiu", "user_agent")
        self.__headers = {"User-Agent": user_agent}

        self.__init_caches(self.__cache_dir)

    def __init_caches(self, path):
        needs_create = True
        if os.path.exists(path):
            if not os.path.isdir(path):
                os.rmtree(path)
            else:
                needs_create = False

        if needs_create:
            os.makedirs(path)

        self.__cache_index_file = "%s/cache_index"%(path)
        cache_index_file = open(self.__cache_index_file, "r")
        cache_index = cache_index_file.read()
        cache_index_file.close()
        if cache_index:
            self.__cache_index = json.loads(cache_index)
        else:
            self.__cache_index = {}

    def __convert_date(self, date):
        return date.replace("/", "-")

    def __process(self, pd):
        # remove 0s
        dates = []
        opens = []
        closes = []
        lows = []
        highs = []
        amounts = []
        for i in range(0, len(pd)):
            if pd.open[i] < 0.01:
                continue;
            dates.append(pd.date[i])
            opens.append(pd.open[i])
            closes.append(pd.close[i])
            lows.append(pd.low[i])
            highs.append(pd.high[i])
            amounts.append(pd.volume[i])

        return pandas.DataFrame({"date": dates, "open": opens, "close": closes,
                                 "low": lows, "high": highs, "amount": amounts})

    def __update_cache_index(self, code, date):
        self.__cache_index[code] = {"update_time": date}
        json_str = json.dumps(self.__cache_index)
        cache_index_file = open(self.__cache_index_file, "w")
        cache_index_file.write(json_str)
        cache_index_file.flush()
        cache_index_file.close()

    def get_hist_data(self, code, is_index = False, use_cache = True):
        if not is_index:
            if code[0] == '6':
                code = "SH%s"%(code)
            else:
                code = "SZ%s"%(code)

        needs_update = True
        csv_path = "%s/%s.csv"%(self.__cache_dir, code)
        if self.__cache_index.has_key(code) and os.path.exists(csv_path):
            cache = self.__cache_index[code]
            if use_cache:
                needs_update = False
            else:
                update_time = cache["update_time"];
                today = datetime.date.fromtimestamp(time.time()).strftime("%Y-%m-%d")
                trade_day = DateHelper().getCurrentTradeDay(today)
                needs_update = (trade_day != update_time)
        else:
            cache = {}

        result = pandas.DataFrame()
        if needs_update:
            url = self.__hist_url%(code)
            r = requests.get(url, headers = self.__headers)
            if r.status_code == 200:
                csv = r.content
                csv_file = open(csv_path, "w")
                csv_file.write(csv)
                csv_file.flush()
                csv_file.close()

                result = pandas.read_csv(csv_path)
                if len(result.date) > 0:
                    date = result.date[len(result.date) - 1]
                    self.__update_cache_index(code, date)
                else:
                    print "%s has no data"%(code)
            else:
                print "failed getting %s with status_code %d"%(code, r.status_code)
        else:
            result = pandas.read_csv(csv_path)

        return self.__process(result)
