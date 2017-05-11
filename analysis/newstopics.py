#Load the news from last 3 days 
from bahutbadhiya.lib.dbutil import DB
from bahutbadhiya.lib.timer import Timer

class News(object):
    def __init__ (self):
        self.db = DB()
        self.articles = None

        #for extracted information
        self.descriptions = None
        self.titles = None

    def fetch(self):
        FETCH_QUERY = "SELECT urlchecksum, url, title, description FROM articles WHERE pubdate > (NOW(-3))"
        self.articles = self.db.results(FETCH_QUERY)

        self.__extract__()
        return self.articles

    def __extract__(self):
        if (self.articles is not None):
            self.descriptions = []
            self.titles = []
            for (urlchecksum, url, title, description) in self.articles:
                self.descriptions.append(description)
                self.titles.append(title)
            
    def __str__(self):
        if (self.descriptions is not None):
            print self.descriptions

        if (self.articles is not None):
            return  u'Number of Articles in Last 3 days == %s' % len(self.articles)
        else:
            print 'No articles fetched'



class Topics(object):
    def __init__(self):
        #stats
        self.analysetime = 0
        self.timer = Timer()

    def analyse(self):
        self.timer.reset()

        self.timer.stop()
        self.analysetime = self.timer.time()


if __name__ == "__main__":

    print "Going to Load the News from Last 3 days"
    news = News()
    news.fetch()

    print news

