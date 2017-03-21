from dbutil import DB
import logging 
import datetime

def init():
    #Configure basic loggign
    FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(filename='error.log',level=logging.DEBUG, format=FORMAT)

def reset_tables(db, name, q_drop, q_create):
    status = db.execute(q_drop)

    if (status):
        logging.info('Dropped old table %s' % (name))
	status = db.execute(q_create)
	if (status):
            logging.info('Created the table %s' % (name))
	else:
            logging.error('Could not create table %s' % (name))
    else:
        logging.error('Could not Drop old table %s' % (name))
        
def initialise_db(db):
    SQL_DROP_FEEDS = "DROP TABLE IF EXISTS feeds"
    SQL_CREATE_FEEDS = """CREATE TABLE feeds (
         id INT NOT NULL AUTO_INCREMENT,
	     urlchecksum CHAR(32),
         url TEXT NOT NULL,
         lastcrawl DATETIME,
         nextcrawl DATETIME,
         crawltime FLOAT,
         responsecode INT,
         numarticle INT,
         numnewarticle INT,
         fetchfailures INT DEFAULT 0,
         parsefailures INT DEFAULT 0,
         freshnessdelta INT, PRIMARY KEY (id) )""" #FRESHNESS DELTA is in minutes (pubdate - lastcrawldate), -ve if we are crawling faster that update
    
    reset_tables(db, 'feeds', SQL_DROP_FEEDS, SQL_CREATE_FEEDS)


    SQL_DROP_ARTICLES = "DROP TABLE IF EXISTS articles"
    SQL_CREATE_ARTICLES = """ CREATE TABLE articles (
                            feedid INT,
                            urlchecksum CHAR(32),
                            url TEXT NOT NULL,
                            contentlink TEXT,
                            title TEXT,
                            description TEXT,
                            pubdate DATETIME,
                            crawldate DATETIME,
                            PRIMARY KEY (urlchecksum))"""
    
    reset_tables(db, 'articles', SQL_DROP_ARTICLES, SQL_CREATE_ARTICLES)

    SQL_DROP_CRAWLS = "DROP TABLE IF EXISTS crawls"
    SQL_CREATE_CRAWLS = """CREATE TABLE crawls (
                                id INT AUTO_INCREMENT,
                                starttime DATETIME,
                                endtime DATETIME,
                                timetaken FLOAT,
                                feedsattempted INT,
                                feedssuccess INT,
                                fetchfailures INT,
                                parsefailures INT,
                                totalarticles INT,
                                newarticles INT, PRIMARY KEY (id))"""


    reset_tables(db, 'crawls', SQL_DROP_CRAWLS, SQL_CREATE_CRAWLS)


def read_feed_file(name):
    try:
 	f = open(name, 'r')
	return filter((lambda x: x != ""), map((lambda x: x.strip()), f.readlines()))
    except Exception, Argument:
	logging.error(Argument)
	return None

def insert_into_db(db, feeds):
    values_list = [(e, e) for e in feeds]
        
    SQL_BATCH = u"INSERT INTO feeds (urlchecksum, url, nextcrawl) VALUES (MD5(%s), %s, \'{}\') ".format(datetime.datetime.now())
    logging.info(SQL_BATCH)
    
    status = db.execute_batch(SQL_BATCH, values_list)
    
    if (status is False):
	   return False
    else:
        return True



if __name__ == '__main__':
    init()
#    db = dbutil.get_db_connection()
#    cursor = db.cursor()
#

    db = DB()
    initialise_db(db)

    feeds = read_feed_file('feeds.txt')
    if feeds is not None:
    	status = insert_into_db(db, feeds)
	if (status is False):
	    logging.error("Could not insert feed urls into DB")
	else:
	    logging.info("inserted %d feed urls into DB" % len(feeds))
    else:
	logging.error('Could not read the feed file')

    del db
    #TODO -- add host name and response code from crawl
