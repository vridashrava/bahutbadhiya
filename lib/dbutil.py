import logging
import MySQLdb
#TODO : add a check to ensure DB connection is still alive, otherwise restart

def init():
    #Configure basic loggign
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='error.log',level=logging.DEBUG, format=FORMAT)

class DB:
    conn = None 
    cursor = None

    def connect(self):
        # Open database connection
        #self.conn = MySQLdb.connect(host="69.89.31.164",user="vichaark_bbadmin",passwd="modi is great",db="vichaark_bblabs", charset='utf8')
        self.conn = MySQLdb.connect(host="news.bahutbadhiya.com",user="bbadmin",passwd="modi is great",db="bahutbadhiya", charset='utf8')
        self.conn.autocommit(True)
        return self.conn

    def __init__(self):
        self.connect()
        self.cursor = self.conn.cursor()

    def execute_batch(self, query, values_list):
        try:
            self.cursor.executemany(query, values_list)
            return True
        except MySQLdb.OperationalError, Argument:
            logging.error(Argument)
            logging.info("Reconnecting database")
            self.connect()
            self.cursor = self.conn.cursor()
            self.cursor.executemany(query, values_list)
        except Exception, Argument:
            logging.error(Argument)
            return False

    #def execute_query (self, statement):
    def execute(self, query):
        #return True if executed False otherwise
        try:
            self.cursor.execute(query)
            return True
        except MySQLdb.OperationalError, Argument:
            logging.error(Argument)
            logging.info("Reconnecting database")
            self.connect()
            self.cursor = self.conn.cursor()
            self.cursor.execute(query)
        except Exception, Argument:
            logging.error(Argument)
            return False



    #def get_db_results(self, query):
    def results(self, query):
        #returns results or Null if not
        try:
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except MySQLdb.OperationalError, Argument:
            logging.error(Argument)
            logging.info("Reconnecting database")
            self.connect()
            self.cursor = self.conn.cursor()
            self.cursor.executemany(sql, values_list)
        except Exception, Argument:
            logging.error(Argument)
            return None



if __name__ == '__main__':
    init()

    #In main routine, open DB connection and print version
    db = DB()

    data = db.get_db_results("SELECT VERSION()")

    print "Database version : %s " % data[0]

