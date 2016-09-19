# -*- coding: utf-8 -*-

import ConfigParser
import MySQLdb
import os
import tushare

from collector import Collector
from consts import *
from store import Store
import crawler

class DBInitializer:
    def __init__(self):
        conf_path = "%s/FDM/FDM.conf"%(os.getcwd())
        self.__conf = ConfigParser.ConfigParser()
        self.__conf.read(conf_path)

        self.__conn = None
        
        self.collector = Collector()

    def start(self):
        host = self.__conf.get("mysql", "host")
        user = self.__conf.get("mysql", "user")
        password = self.__conf.get("mysql", "password")
        charset = self.__conf.get("mysql", "charset")
        db = self.__conf.get("mysql", "db")

        mysql_path = "mysql:"
        self.__conn = MySQLdb.connect(host = host, user = user,
                                    passwd = password, charset = charset)

        cursor = self.__conn.cursor()
        try:
            cursor.execute("use %s"%(db))
        except:
            cursor.execute("create database %s default character set utf8"%(db))
            cursor.execute("use %s"%(db))

        cursor.close()
        self.__do_init(self.__conn)
    
    def __do_init(self, conn):
        self.__maybe_init_stocks_table(conn)
        self.__maybe_init_bonus_table(conn)
        self.__maybe_init_finance_table(conn)
        self.__maybe_init_market_table(conn)

    def __maybe_init_stocks_table(self, conn):
        cursor = conn.cursor()
        if cursor.execute('show tables like "stock_information"') == 0:
            print "init stock information..."
            sql_path = "%s/FDM/sqls/create_stocks_table.sql"%(os.getcwd())
            sql_file = open(sql_path, "r")
            create_table_sql = sql_file.read()
            sql_file.close()
            cursor.execute(create_table_sql)

            self.collector.collect_stock_information()
        cursor.close()

    def __maybe_init_bonus_table(self, conn):
        cursor = conn.cursor()
        if cursor.execute('show tables like "bonus"') == 0:
            print "init bonus..."
            sql_path = "%s/FDM/sqls/create_bonus_table.sql"%(os.getcwd())
            sql_file = open(sql_path, "r")
            create_bonus_sql = sql_file.read()
            sql_file.close()
            cursor.execute(create_bonus_sql)

            self.collector.collect_bonus()
        cursor.close()

    def __maybe_init_finance_table(self, conn):
        cursor = conn.cursor()
        if cursor.execute('show tables like "finance"') == 0:
            print "init finance..."
            sql_path = "%s/FDM/sqls/create_finance_table.sql"%(os.getcwd())
            sql_file = open(sql_path, "r")
            create_finance_sql = sql_file.read()
            sql_file.close()
            cursor.execute(create_finance_sql)

            self.collector.collect_finance()
        cursor.close()

    def __maybe_init_market_table(self, conn):
        cursor = conn.cursor()
        if cursor.execute('show tables like "market"') == 0:
            print "init market..."
            sql_path = "%s/FDM/sqls/create_market_table.sql"%(os.getcwd())
            sql_file = open(sql_path, "r")
            create_table_sql = sql_file.read()
            sql_file.close()
            cursor.execute(create_table_sql)

            self.collector.collect_market(XUEQIU)
        cursor.close()

    def __del__(self):
        if self.__conn:
            self.__conn.close()

