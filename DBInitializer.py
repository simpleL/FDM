# -*- coding: utf-8 -*-

import ConfigParser
import MySQLdb
import os

class DBInitializer:
    def __init__(self):
        conf_path = "%s/FDM/FDM.conf"%(os.getcwd())
        self.__conf = ConfigParser.ConfigParser()
        self.__conf.read(conf_path)

        self.__conn = None

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
            cursor.execute("create database %s"%(db))
            cursor.execute("use %s"%(db))

        self.__do_init(cursor)
    
    def __do_init(self, cursor):
        print("do_init")

    def __del__(self):
        if self.__conn:
            self.__conn.close()

