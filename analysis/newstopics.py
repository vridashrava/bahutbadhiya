#Load the news from last 3 days 
from bahutbadhiya.lib.dbutil import DB
from bahutbadhiya.lib.timer import Timer

#For topic modelling using sci-kit learn
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.datasets import fetch_20newsgroups
from sklearn.decomposition import NMF, LatentDirichletAllocation


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

    def __extract__(self):
        if (self.articles is not None):
            self.descriptions = []
            self.titles = []
            for (urlchecksum, url, title, description) in self.articles:
                self.descriptions.append(description)
                self.titles.append(title)
            
    def __str__(self):

        if (self.articles is not None):
            return  u'Number of Articles in Last 3 days == %s' % len(self.articles)
        else:
            print 'No articles fetched'
            
    def descriptions(self):
        return self.descriptions
    
    def titles(self):
        return self.titles



class TopicsModel(object):
    def __init__(self, data):
        #stats
        self.analysetime = 0
        self.timer = Timer()
        self.data = data
        
        #Model specific data
        self.numfeatures = 1000 
        self.numtopics = 10
        self.model = None
        self.featurenames = None
        
        #display params
        self.numtopwords = 10

    def analyse(self, isLDA = True):
        self.timer.reset()
        
        if (isLDA):
            # LDA can only use raw term counts, is a probabilistics
            # graphical model
            tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=self.numfeatures, stop_words='english')
            tf = tf_vectorizer.fit_transform(documents)
            self.featurenames = tf_vectorizer.get_feature_names()
            
            #RUN
            self.model = LatentDirichletAllocation(n_topics=self.numtopics, max_iter=5, learning_method='online', learning_offset=50.,random_state=0).fit(tf)
            
        else:
            #Use NMF : able to use TF IDF
            tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, max_features=self.numfeatures, stop_words='english')
            tfidf = tfidf_vectorizer.fit_transform(documents)
            self.featurenames = tfidf_vectorizer.get_feature_names()
            
            #RUN
            self.model = NMF(n_components=self.numtopics, random_state=1, alpha=.1, l1_ratio=.5, init='nndsvd').fit(tfidf)
            
        self.timer.stop()
        self.analysetime = self.timer.time()
        
    #def data(self, d = )
    def display (self):
        if (self.model is not None):
            for topic_idx, topic in enumerate(self.model.components_):
                print "Topic %d:" % (topic_idx)
                print " ".join([self.featurenames[i]
                            for i in topic.argsort()[:-self.numtopwords - 1:-1]])
                
        print "Total time taken : %s seconds" % (self.analysetime)



if __name__ == "__main__":

    print "Going to Load the News from Last 3 days"
    news = News()
    news.fetch()

    print news


    # Sample data
    dataset = fetch_20newsgroups(shuffle=True, random_state=1, remove=('headers', 'footers', 'quotes'))
    
    documents = dataset.data
    t = news.titles()
    if (t is not None):
        documents = t
    else:
        print "Titles were None"
    
    for t in documents:
        print t
        
    t = TopicsModel(documents)
    t.analyse(False)
    t.display()
    
