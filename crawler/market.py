import datetime
import json
import random
import requests
import pandas

def get_h_data(code, start, end):
    sohu_hq_url = "http://q.stock.sohu.com/hisHq?code=cn_%s&start=%s&end=%s&stat=1&order=D&period=d&callback=historySearchHandler&rt=jsonp&r=%.16f"
    start_string = datetime.datetime.strptime(start, "%Y-%m-%d").strftime("%Y%m%d")
    end_string = datetime.datetime.strptime(end, "%Y-%m-%d").strftime("%Y%m%d")
    url = sohu_hq_url%(code, start_string, end_string, random.random())
    
    r = requests.get(url)
    json_start = r.text.index("(") + 1
    json_end = r.text.rindex(")")
    json_string = r.text[json_start:json_end]
    
    result = json.loads(json_string)
    
    trade = []
    
    if len(result) > 0 and result[0]["status"] == 0: 
        hq = result[0]["hq"]
        for daily in hq:
            dict = {}
            dict["date"] = daily[0].encode("utf8")
            dict["open"] = daily[1].encode("utf8")
            dict["close"] = daily[2].encode("utf8")
            dict["low"] = daily[5].encode("utf8")
            dict["high"] = daily[6].encode("utf8")
            dict["volume"] = int(float(daily[7].encode("utf8")) * 100)
            dict["amount"] = int(float(daily[8].encode("utf8")) * 10000)
            
            trade.append(dict)
    
    else:
        print code
    
    if len(trade) > 0:
        df = pandas.DataFrame(trade)
        df = df.set_index("date")
        return df
         
    return None
