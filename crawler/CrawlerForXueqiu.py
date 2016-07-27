# -*- coding: utf-8 -*-

import ConfigParser
import datetime
import json
import os
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
        if os.path.exists(self.__cache_index_file):
            cache_index_file = open(self.__cache_index_file)
            cache_index = cache_index_file.read()
            self.__cache_index = json.loads(cache_index)
            cache_index_file.close()
        else:
            self.__cache_index = {}
        print self.__cache_index

    def __convert_date(self, date):
        return date.replace("/", "-")

    def get_hist_data(self, code, is_index = False, use_cache = True):
        if not is_index:
            if code[0] == '6':
                code = "SH%s"%(code)
            else:
                code = "SZ%S"%(code)

        needs_update = True
        cache = self.__cache_index[code]
        if cache:
            if use_cache:
                needs_update = False
            else:
                update_time = cache.update_time;
                today = datetime.date.fromtimestamp(time.time()).strftime("%Y-%m-%d")
                needs_update = (today == updatetime)
        else:
            cache = {}

        if needs_update:
            url = self.__hist_url%(code)
            r = requests.get(url, headers = self.__headers)



