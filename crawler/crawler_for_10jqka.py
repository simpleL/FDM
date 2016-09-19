# -*- coding: utf-8 -*-

import ConfigParser
import datetime
import json
import os
import pandas
import requests
import time
import xlrd

from ..utils import DateHelper

class CrawlerFor10JQKA:
    def __init__(self):
        conf_path = "%s/FDM/crawler/10jqka.conf"%(os.getcwd())
        self.__conf = ConfigParser.ConfigParser()
        self.__conf.read(conf_path)
        self.__finance_url = self.__conf.get("10jqka", "finance_url")
        cache_dir = self.__conf.get("10jqka", "cache_dir")
        self.__cache_dir = "%s/%s"%(os.getcwd(), cache_dir)
        
        user_agent = self.__conf.get("10jqka", "user_agent")
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
        try:
            cache_index_file = open(self.__cache_index_file, "r")
            cache_index = cache_index_file.read()
            cache_index_file.close()
            self.__cache_index = json.loads(cache_index)
        except:
            self.__cache_index = {}

    def __get_double(self, number):
        if type(number) == type("") or type(number) == type(u""):
            return 0
        return number

    def __process_finance_excel(self, code, excel_path):
        #excel_path = "C:\\Users\\linsihua\\Downloads\\mainreport.xls"
        print excel_path
        arr = []
        data = xlrd.open_workbook(excel_path)
        if data is None or len(data.sheets()) < 2:
            return pandas.DataFrame()
        sheet = data.sheets()[0]
        for i in range(1, sheet.ncols):
            dict = {}
            dict["date"] = sheet.col_values(i)[0]
            dict["code"] = code
            dict["earning_per_share"] = self.__get_double(sheet.col_values(i)[1])
            dict["net_margin"] = self.__get_double(sheet.col_values(i)[2])
            dict["nonrecurring_net_margin"] = self.__get_double(sheet.col_values(i)[4])
            dict["total_income"] = self.__get_double(sheet.col_values(i)[5])
            dict["asset_per_share"] = self.__get_double(sheet.col_values(i)[7])
            dict["roe"] = self.__get_double(sheet.col_values(i)[8])
            dict["diluted_roe"] = self.__get_double(sheet.col_values(i)[9])
            dict["debt_ratio"] = self.__get_double(sheet.col_values(i)[10])
            dict["fund_per_share"] = self.__get_double(sheet.col_values(i)[11])
            dict["undistributed_profit_per_share"] = self.__get_double(sheet.col_values(i)[12])
            dict["cash_flow_per_share"] = self.__get_double(sheet.col_values(i)[13])
            arr.append(dict)
            
        result = pandas.DataFrame(arr)
        return result

    def __update_cache_index(self, code, date):
        self.__cache_index[code] = {"update_finance_time": date}
        json_str = json.dumps(self.__cache_index)
        cache_index_file = open(self.__cache_index_file, "w")
        cache_index_file.write(json_str)
        cache_index_file.flush()
        cache_index_file.close()

    def __get_finance_data(self, code, use_cache = True):
        needs_update = True
        excel_path = "%s/%s_finance.xls"%(self.__cache_dir, code)
        today = datetime.date.fromtimestamp(time.time()).strftime("%Y-%m-%d")
        if self.__cache_index.has_key(code) and os.path.exists(excel_path):
            cache = self.__cache_index[code]
            if use_cache:
                needs_update = False
            else:
                update_time = cache["update_finance_time"];
                needs_update = (today != update_time)
        else:
            cache = {}

        result = pandas.DataFrame()
        if needs_update:
            url = self.__finance_url%(code)
            retry_count = 3
            excel = None
            for i in range(0, retry_count):
                try:
                    r = requests.get(url, headers = self.__headers, timeout = 5)
                except:
                    print "getting %s finance data timeout..."%(code)
                else:
                    excel = r.content
                    break
            if excel:
                excel_file = open(excel_path, "wb")
                excel_file.write(excel)
                excel_file.flush()
                excel_file.close()

                result = self.__process_finance_excel(code, excel_path)
                if len(result) > 0:
                    self.__update_cache_index(code, today)
                else:
                    print "%s has no data"%(code)
            else:
                print "failed getting %s with status_code %d"%(code, r.status_code)
        else:
            result = self.__process_finance_excel(code, excel_path)

        return result

    def get_finance_data(self, code):
        trades = self.__get_finance_data(code, use_cache = False)
        return trades