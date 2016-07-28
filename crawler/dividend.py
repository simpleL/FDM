# -*- coding:utf-8 -*-

import datetime
import requests
import lxml.html
import pandas
import HTMLParser

def get_dividend(code):
    request_url = "http://money.finance.sina.com.cn/corp/go.php/vISSUE_ShareBonus/stockid/{code}.phtml".format(code = code)
    #r = requests.get(request_url)
    
    html = lxml.html.parse(request_url)
    dom = html.xpath("//table[@id=\"sharebonus_1\"]/tbody")
    
    res = pandas.DataFrame({"announce_date": [], "stat_right_date": [],
                            "exright_date": [], "dividend": [],
                            "bonus_stock": [], "tranadd_stock": []})
    
    td_count = 0
    for element in dom[0].iter():
        if element.tag == "td":
            td_count = td_count + 1
    
    if (td_count < 9):
        return res
    
    count = 0
    dict = {}
    for element in dom[0].iter():
        if element.tag == "td":
            """
            0 -> announce_date
            6 -> stat_right_date
            5 -> exright_date
            3 -> dividend
            1 -> bonus_stock
            2 -> tranadd_stock
            4 -> ʵʩ
            """
            index = count % 9
            if index == 0:
                if dict.has_key("act") and dict["act"] == u"ʵʩ".encode("utf-8"):
                    del dict["act"]
                    dict["code"] = code
                    res = res.append(dict, ignore_index = True)
                dict = {}
                date = "1900-01-01"
                if element.text != "--":
                    date = element.text
                dict["announce_date"] = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            elif index == 1:
                dict["bonus_stock"] = element.text
            elif index == 2:
                dict["tranadd_stock"] = element.text
            elif index == 3:
                dict["dividend"] = element.text
            elif index == 4:
                dict["act"] = element.text.encode("gbk")
                
            elif index == 5:
                date = "1900-01-01"
                if element.text != "--":
                    date = element.text
                dict["exright_date"] = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            elif index == 6:
                date = "1900-01-01"
                if element.text != "--":
                    date = element.text
                dict["stat_right_date"] = datetime.datetime.strptime(date, "%Y-%m-%d").date()
            count = count + 1
    
    if dict.has_key("act") and dict["act"] == u"ʵʩ".encode("utf-8"):
        del dict["act"]
        dict["code"] = code
        res = res.append(dict, ignore_index = True)
    
    return res
