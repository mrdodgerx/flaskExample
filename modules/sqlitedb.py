import sqlite3

class SqliteDb():
    def __init__(self, path="config.db") -> None:
        self.db_path = path
        self.conn = None
        self.connect()
        
    def connect(self):
        try:
            self.conn = sqlite3.connect(self.db_path)
        except Exception as err:
            print("Error sqlite Connect, Error: ", err)
            self.conn.close()
            
    def query(self, sql="", args=(), one=False):
        cur = self.conn.cursor()
        cur.execute(sql, args)

        r = [dict((cur.description[i][0], value) \
                  for i, value in enumerate(row)) for row in cur.fetchall()]
        cur.connection.close()

        return (r[0] if r else None) if one else r
    
    def execute(self, sql, args=()):
        cur = self.conn.cursor()
        cur.execute(sql, args)
    
    def commit(self):
        self.conn.commit()
            
    def close(self):
        self.conn.close()