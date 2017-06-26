#Load the news from last 3 days 
from bahutbadhiya.lib.dbutil import DB
from bahutbadhiya.lib.timer import Timer

#For topic modelling using sci-kit learn
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.datasets import fetch_20newsgroups
from sklearn.decomposition import NMF, LatentDirichletAllocation
import numpy as np

import sys


class News(object):
    def __init__ (self):
        self.db = DB()
        self.articles_db = None
        self.articles = []
        #for extracted information
        self.descriptions = None
        self.titles = None
        

    def fetch(self):
        FETCH_QUERY = "SELECT urlchecksum, url, title, description FROM articles WHERE pubdate > (NOW(-3))"
        self.articles_db = self.db.results(FETCH_QUERY)

        self.__extract__()

    def __extract__(self):
        if (self.articles_db is not None):
            self.descriptions = []
            self.titles = []
            for (urlchecksum, url, title, description) in self.articles_db:
                self.descriptions.append(description)
                self.titles.append(title)
                
                #save the article for future reference
                self.articles.append(Article(url, urlchecksum, title, description))
            
    def __str__(self):

        if (self.articles is not None):
            return  u'Number of Articles in Last 3 days == %s' % len(self.articles)
        else:
            print 'No articles fetched'
            
    def get_article(self, idx):
        if (idx < len(self.articles)):
            return self.articles[idx]
        else:
            return None

class Article(object):
    
    def __init__(self, url, urlchecksum, title, description):
        self.urlchecksum = urlchecksum
        self.url = url
        self.title = title
        self.description = description
        
    def __str__(self):
        return u'%s: %s (%s)' % (self.urlchecksum, self.title, self.url)
    
    
class Topic(object):
    
    def __init__(self, topicnum):
        self.topicnum = topicnum
        self.articles = []
        
    def setfeatures(self, features):
        self.features = features
        
        
    def addArticle(self, article):
        self.articles.append(article)
        
    def display(self):
        print "Topic: %s" % self.topicnum
        print "Features [%s]" % self.features
        print "--------------------------------"
        
        for a in self.articles:
            p = "\t %s" %a
            print p.encode('utf-8')
            #print u"\t %s" % a


class TopicModelling(object):
    
    
    def __init__(self, articles, useTitles = True, useSample = False):
        self.useTitles = useTitles
        #stats
        self.analysetime = 0
        self.timer = Timer()
        
        #extract data from the articles
        if (not useSample):
            self.articles = articles
            self.data = []
            self.__extract_data()
        else:
            self.articles = None
            self.data = articles
        
        #Model specific data
        self.numfeatures = 1000 
        self.numtopics = 10
        self.model = None
        self.featurenames = None
        
        #display params
        self.numtopwords = 10
        
        #topic clusters
        self.topics = []
        
    def __extract_data(self):
        for a in self.articles:
            if (self.useTitles):
                self.data.append(a.title)
            else:
                if (a.description is not None):
                    self.data.append(a.description)
                else:
                    self.data.append(a.title)
        

    def analyse(self, isLDA = True, numTopics = 10):
        self.timer.reset()
        self.numtopics = numTopics
        
        if (isLDA):
            # LDA can only use raw term counts, is a probabilistics
            # graphical model
            tf_vectorizer = CountVectorizer(max_df=0.95, min_df=2, max_features=self.numfeatures, stop_words='english')
            tf = tf_vectorizer.fit_transform(self.data)
            self.featurenames = tf_vectorizer.get_feature_names()
            
            #RUN
            self.model = LatentDirichletAllocation(n_topics=self.numtopics, max_iter=50, learning_method='online', learning_offset=50.,random_state=0).fit(tf)
            
            # unnormalized doc-topic distribution
            self.doc_topic_dist_unnormalized = np.matrix(self.model.transform(tf))
        else:
            #Use NMF : able to use TF IDF
            tfidf_vectorizer = TfidfVectorizer(max_df=0.95, min_df=2, max_features=self.numfeatures, stop_words='english')
            tfidf = tfidf_vectorizer.fit_transform(self.data)
            self.featurenames = tfidf_vectorizer.get_feature_names()
            
            #RUN
            self.model = NMF(n_components=self.numtopics, random_state=1, alpha=.1, l1_ratio=.5, init='nndsvd').fit(tfidf)
            
            # unnormalized doc-topic distribution
            self.doc_topic_dist_unnormalized = np.matrix(self.model.transform(tfidf))
            
        self.timer.stop()
        self.analysetime = self.timer.time()
        
    #def data(self, d = )
    def display (self):
        #if (self.model is not None):
        #    for topic_idx, topic in enumerate(self.model.components_):
        #        print "Topic %d:" % (topic_idx)
        #        print " ".join([self.featurenames[i]
        #                    for i in topic.argsort()[:-self.numtopwords - 1:-1]])
        
        for t in self.topics:
            t.display()
                
        print "Total time taken : %s seconds" % (self.analysetime)

    def documentToTopic(self):
        #create topics from the model
        for topic_idx, topic in enumerate(self.model.components_):
            topic_features = [self.featurenames[i] for i in topic.argsort()[:-self.numtopwords - 1:-1]]
            topic = Topic(topic_idx)
            topic.setfeatures(topic_features)
             
            self.topics.append(topic)
            #print "Added Topic %d with features %s" % (topic_idx, self.topics[topic_idx].features)
        
        # normalize the distribution (only needed if you want to work with the probabilities)
        self.doc_topic_dist = self.doc_topic_dist_unnormalized/self.doc_topic_dist_unnormalized.sum(axis=1)
        
        # predict topics for test data (use the top ranking topic)
        t = self.doc_topic_dist.argmax(axis=1)
        
        for idx, topic in enumerate (t):
            self.topics[topic.item(0,0)].addArticle(self.articles[idx])
            #print idx, topic.item(0,0), u'%s' % (self.articles[idx])

def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")

if __name__ == "__main__":
    
    useSample = False

    if (useSample): #current code will not work with data not in article format
        # Sample data
        dataset = fetch_20newsgroups(shuffle=True, random_state=1, remove=('headers', 'footers', 'quotes'))
        documents = dataset.data
    else:
        print "Going to Load the News from Last 3 days"
        news = News()
        news.fetch()
        documents = news.articles

        print news
        
    useLDA = True
    numTopics = 20
    
    if (len(sys.argv) > 1):
        numTopics = int(sys.argv[1])
        
        if (len(sys.argv) > 2): 
            useLDA = str2bool(sys.argv[2])
    
    print "Going to analyse %s topics." % (numTopics)
    if (useLDA): 
        print "Using the Latent Dirichlet Allocation Model"
    else:
        print "Using the Non-negative matrix factorization Model"
        
    tm = TopicModelling(documents, False)
    tm.analyse(useLDA, numTopics)
    tm.documentToTopic()
    tm.display()
    
