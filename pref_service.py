# -*- coding: utf-8 -*-

import json
import os

class PrefService:
    pref_path = "%s/FDM Data/preferences"%(os.getcwd())
    def __read_dict(cls):
        dict = {}
        try:
            file = open(PrefService.pref_path, "r")
            json_string = file.read()
            file.close()
            dict = json.loads(json_string)
            return dict
        except:
            return {}
            
    def __write_dict(cls, dict):
        json_string = json.dumps(dict)
        file = open(PrefService.pref_path, "w")
        file.write(json_string)
        file.flush()
        file.close()
    
    def get_value(cls, key, default = None):
        dict = cls.__read_dict()
        
        value = default
        if dict.has_key(key):
            value = dict[key]
            
        return value
        
            
    def set_value(cls, key, value):
        dict = cls.__read_dict()
        dict[key] = value
        cls.__write_dict(dict)