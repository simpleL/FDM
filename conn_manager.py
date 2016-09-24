import MySQLdb

class ConnManager:
    conn = None
    def get_conn(cls):
        if conn is None:
            conn = MySQLdb.connect("127.0.0.1", "root", "root", "quant", charset = "utf8")
        
        try:
            conn.ping()
        except:
            conn = MySQLdb.connect("127.0.0.1", "root", "root", "quant", charset = "utf8")
        
        return conn