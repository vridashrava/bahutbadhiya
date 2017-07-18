#from bahutbadhiya.lib import dbutil
import logging
import datetime
import requests
import feedparser
import md5
from multiprocessing import Pool
from dateutil.parser import parse
from bahutbadhiya.lib.dbutil import DB
from bahutbadhiya.lib.timer import Timer

#TODO: use decorators for timing


WORKER_POOL_SIZE = 10

def init():
    #Configure basic loggign
    FORMAT = "[%(asctime)s: %(filename)s:%(lineno)s - %(funcName)20s() ] [%(levelname)s] %(message)s"
    logging.basicConfig(filename='error.log',level=logging.DEBUG, format=FORMAT)

def crawl_feeds((url, urlchecksum, feedid, fetchfailures, parsefailures)):
    logging.info("Inside crawl_feed function for feed[%s] %s" % (feedid, url))
    db = DB() #TODO: see if we can use a Pool here
    f = Feed(url, feedid, urlchecksum, fetchfailures, parsefailures)
    if (f.isHealthy()):
        f.push_to_db(db)
        f.update_db_stats(db)
    else:
        logging.error("Problem fetching/parsing Feed [%s]: %s" % (feedid, url))
        f.update_db_stats(db)

    del db
    return f.stats


class FeedCrawler(object):
    def __init__(self):
       self.db = DB()
       self.feeds = None

       #stats
       self.feedsfetched = 0
       self.feedsSuccess = 0
       self.articlestotal = 0
       self.articlesnew = 0
       self.crawltime = 0
       self.fetchfailures = 0
       self.parsefailures = 0

       #timer
       self.timer = Timer()
       self.starttime = datetime.datetime.now()

    def new_articles_found(self):
        try:
            SQL = "SELECT count(*) FROM articles WHERE crawldate >= \'%s\'" % (self.starttime)
            count = self.db.results(SQL)
            return count[0][0]

        except Exception, Argument:
            logging.error(Argument)
            return -1


    def generate_feedlist(self):

        SQL = "SELECT url, urlchecksum, id, fetchfailures, parsefailures from feeds where nextcrawl < \'%s\' and fetchfailures < 3 and parsefailures < 3" % (datetime.datetime.now()) 
       
        try:
             self.feeds = self.db.results(SQL)
             return self.feeds
        except Exception, Argument:
            logging.error(Argument)
            return None

    def update_stats(self, stats):
        self.feedsfetched += 1
        if (stats.responseCode == 200): 
            self.feedsSuccess += 1
            self.articlestotal += stats.numfeeds
            self.articlesnew += stats.newinlastCrawl

            if (stats.failedparse): self.parsefailures += 1
        
        if (stats.failedfetch):
            self.fetchfailures += 1

    def crawl(self):
        if self.feeds is not None:
            self.timer.reset()
            logging.info( "Got %s feeds to crawl: " % (len(self.feeds)))
            logging.info("Creating a pool of %s workers" % WORKER_POOL_SIZE)
            p = Pool (WORKER_POOL_SIZE)

            crawled_stats = p.map(crawl_feeds, self.feeds)

            #Collects stats from the feeds
            for stat in crawled_stats:
                self.update_stats(stat)

            del p

            self.articlesnew = self.new_articles_found()    #HACK: Reading by selecting count of articles inserted post the starttime
            self.timer.stop()
            self.crawltime = self.timer.time()
            self.update_stats_db()

            print self
            return True
        else:
	    logging.error("Could not obtain the list of feeds to crawl, exititing")
            return False

    def __str__(self):
        return u'[crawltime: %s secs] [total feeds: %s] [success feeds: %s] [total articles: %s] [new articles: %s] [failures(fetch/parse): (%s/%s)' % (self.crawltime, self.feedsfetched, self.feedsSuccess, self.articlestotal, self.articlesnew, self.fetchfailures, self.parsefailures)

    def update_stats_db(self):
        try:
            endtime = datetime.datetime.now()
            SQL = """INSERT INTO crawls 
                           (starttime, endtime, timetaken, feedsattempted, feedssuccess, 
                              fetchfailures, parsefailures, totalarticles, newarticles) 
                           VALUES (\'%s\', \'%s\', %s, %s, %s, %s, %s, %s, %s)  
                   """ % (self.starttime, endtime, self.crawltime, self.feedsfetched, self.feedsSuccess, 
                                self.fetchfailures, self.parsefailures, self.articlestotal, self.articlesnew)

            #logging.debug(SQL)
            self.db.execute(SQL)
            logging.info("Updated stats in DB for the crawl")
        except Exception, Argument:
            logging.error(Argument)
 
 

class FeedEntry(object):
    #TODO datetimes have to be standardised to a fixed timezone
    
    def __init__(self, d):
        self.title = d.title
        self.url = d.link
        self.description = d.description if (d.has_key('description')) else None
        #default pubdate to now (discovery time) if not present
        self.pubdate = parse(d.published).strftime('%Y-%m-%d %H:%M:%S') if (d.has_key('published')) else None
        self.crawldate = datetime.datetime.now()
        
    def __str__(self):
        return u'%s [%s, %s]\n%s\n%s' % (self.title, self.pubdate, self.crawldate, self.url, self.description)
    
    def db_value(self, feedid):
        return (feedid, md5.new(self.url).hexdigest(), self.url, self.title.encode('utf-8'), self.description.encode('utf-8'), self.pubdate, self.crawldate)
    
class FeedStats (object):
    
    def __init__(self, url, urlchecksum, feedid, fetchfailures, parsefailures):
        self.url = url
        self.checksum = urlchecksum
        self.feedid = feedid
        self.responseCode = 0
        self.crawltime = 0
        self.numfeeds = 0
        self.newinlastCrawl = 0
        self.failedfetch = False
        self.failedparse = False
        self.numfailedfetch = fetchfailures
        self.numfailedparse = parsefailures

    def set_code(self, code):
        self.responseCode = code

    def set_time(self, time):
        self.crawltime = time

    def set_numfeeds(self, num):
        self.numfeeds = num

    #TODO: to add bloomfilter to get this
    def set_numnew(self, new):
        self.newinlastCrawl = new

    def add_failedfetch(self):
        self.failedfetch = True
        self.numfailedfetch += 1

    def add_failedparse(self):
        self.failedparse = True
        self.numfailedparse += 1

    def __str__(self):
        return u'%s: [%s] -- [code: %s] [time: %s] [feeds: %s] [new: %s] [fetchfail: %s] [parsefail: %s]' % (self.checksum, self.url, self.responseCode, self.crawltime, self.numfeeds, self.newinlastCrawl, self.numfailedfetch, self.numfailedparse)

    def write_to_db(self, db):
        try:
            nowtime = datetime.datetime.now()
            nextime = nowtime + datetime.timedelta(minutes=1)
            SQL = """UPDATE feeds SET lastcrawl = \'%s\', 
                                      nextcrawl = \'%s\', 
                                      crawltime = %s,
                                      responsecode = %s,
                                      numarticle = %s,
                                      numnewarticle = %s,
                                      fetchfailures = %s,
                                      parsefailures = %s
                                  WHERE urlchecksum = \'%s\'
                   """ % (nowtime, nextime, self.crawltime, self.responseCode, self.numfeeds, self.newinlastCrawl, self.numfailedfetch, self.numfailedparse, self.checksum)
            #logging.debug(SQL)
            db.execute(SQL)
            logging.info("Updated stats in DB for feed %s" %(self.feedid))
        except Exception, Argument:
            logging.error(Argument)
 
    
class Feed(object):
    #TODO auto populate missing fields (pubdate, etc) from the data
    #TODO URLs have to be canonicalised
    #FEEds also have category information, check out



    def __init__(self, url, feedid, urlchecksum, fetchfailures, parsefailures):
        self.url = url
        self.feedid = feedid
        self.stats = FeedStats(url, urlchecksum, feedid, fetchfailures, parsefailures)


        self.init()


    def isHealthy(self):
        return self.status
        
    def fetch(self):
        try:
            logging.info('Fetching url %s' % (self.url))
            headers = requests.utils.default_headers()
            headers.update({'User-Agent': 'BB Labs Feed Crawl 1.0', })

            t = Timer()
            r = requests.get(self.url, headers=headers)
            t.stop()

            self.content = r.content
            self.stats.set_code(r.status_code)
            self.stats.set_time(t.time())

            if (r.status_code == requests.codes.ok):
                return True
            else:
                self.stats.add_failedfetch()
                return False

            #logging.info(self.content)
        except Exception, Argument:
            logging.error(Argument)
            self.stats.add_failedfetch()
            return False

    def parse(self):
        try:
            f = feedparser.parse(self.content)
            self.title = f.feed.title
            self.description = f.feed.description

            if (f.feed.has_key('published')):
                self.pubdate = f.feed.published
                
            self.entries = map((lambda x: FeedEntry(x)), f.entries)

            self.stats.set_numfeeds (len(self.entries))
            return True


        except Exception, Argument:
            logging.error(Argument)
            self.stats.add_failedparse()
            return False

    def init(self):
        self.content = None
        self.title = None
        self.description = None
        self.pubdate = None
        self.entries = []
        self.status = False
        
        self.status = self.fetch()
        if (self.status): self.status = self.parse()

        logging.info(self.stats) 

        
    def _print(self):
        print u'%s [%s]' % (self.title, self.pubdate)
        print self.url
        print self.description
        print '----------------------------------------'
        
        for e in self.entries:
            print u'[%s] %s' % (e.pubdate, e.title)

    def update_db_stats(self, db):
        self.stats.write_to_db(db)
           
    def push_to_db(self, db):
        try:
            SQL_BATCH = """INSERT IGNORE INTO articles (feedid, urlchecksum,url, title, description, pubdate, crawldate)
                        VALUES (%s, %s, %s, %s, %s, %s, %s) """

            values_list = [e.db_value(self.feedid) for e in self.entries]
            logging.info("Inserting %s articles for Feed %s" % (len(values_list), self.url))
            #logging.info(values_list)
            db.execute_batch(SQL_BATCH, values_list)
            return True
        except Exception, Argument:
            logging.error(Argument)
            return False

if __name__ == '__main__':
    init()

    crawler = FeedCrawler()
    crawler.generate_feedlist()

    if (crawler.crawl()):
        print 'Crawl Successful'
    else:
        print 'Crawl Failed'



