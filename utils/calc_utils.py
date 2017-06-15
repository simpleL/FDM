# -*- coding:utf-8 -*- 

import datetime
import math
from ..consts import *

class CalcUtils:
    def get_surge_limit(cls, price):
        new_price = price * 1.1
        temp_price = round(new_price * 100.0 + 0.01)
        new_price = temp_price / 100.0
        return new_price

    def get_decline_limit(cls, price):
        new_price = price * 0.9
        temp_price = round(new_price * 100.0 + 0.01)
        new_price = temp_price / 100.0
        return new_price
    
    def get_change_type(cls, trade):
        last_close = float(trade.last_close)
        open = float(trade.close)
        close = float(trade.close)
        high = float(trade.high)
        low = float(trade.low)
        if (close > last_close + 0.001):
            surge_limit = cls.get_surge_limit(last_close)
            if abs(high - surge_limit) < 0.001:
                if abs(close - surge_limit) < 0.001:
                    if abs(low - surge_limit) < 0.001:
                        return YIZI_ZT
                    else:
                        return ZT
                else:
                    return ZT_FAIL
            else:
                return RISE
        elif (close < last_close - 0.001):
            decline_limit = cls.get_decline_limit(last_close)
            if abs(low - decline_limit) < 0.001:
                if abs(close - decline_limit) < 0.001:
                    if abs(high - decline_limit) < 0.001:
                        return YIZI_DT
                    else:
                        return DT
                else:
                    return DT_FAIL
            else:
                return FALL
        else:
            return FLAT

    def exright(cls, bonus, last_close):
        price = last_close
        factor = 1.0
        price = float(last_close) - float(bonus.dividend) / 10.0
        price = price * 10.0 / float(bonus.tranadd_stock + bonus.bonus_stock + 10)
        factor = price / float(last_close)

        return {"price": price, "factor": factor}

    def trim_float(cls, value):
        if type(value) == str:
            try:
                value = float(value)
            except:
                value = 0
        try:
            return math.ceil(value * 100) / 100.
        except:
            return 0