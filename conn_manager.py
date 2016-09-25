import MySQLdb

class ConnManager:
    __conn = None
    @classmethod
    def get_conn(cls):
        if ConnManager.__conn is None:
            ConnManager.__conn = MySQLdb.connect("127.0.0.1", "root", "root", "quant", charset = "utf8")
        
        try:
            ConnManager.__conn.ping()
        except:
            ConnManager.__conn = MySQLdb.connect("127.0.0.1", "root", "root", "quant", charset = "utf8")
        
        return ConnManager.__conn