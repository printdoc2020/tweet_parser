from pprint import pformat
import collections
import re

# Data manipulation
import pandas as pd
from gensim.models.doc2vec import Doc2Vec, TaggedDocument
# from spellchecker import SpellChecker

from nltk.tokenize import RegexpTokenizer
from nltk import pos_tag
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords
from gensim.parsing.preprocessing import STOPWORDS
import numpy as np
import json
class Tweet:
    tweet_type = {"original_tweet":1,
                  "retweet": 2,
                  "quotetweet": 3}

    social_media_type = {
        "facebook": 1,
        "twitter": 2,
        "tiktok": 3,
        "pinterest": 4,
        "youtube": 5,
        "instagram": 6,
        "reddit": 7,
        "snapchat": 8,
        "whatsapp": 9,
        "other":10,
        "none":-1
    }

    illustration_type = {
        "image": 1,
        "video": 3,
        "gif": 4,
        "other": 2,
        "none": -1

    }

    def __init__(self ):
        self.data = dict()
        self.stop_words = set(STOPWORDS).union(stopwords.words("english"))\
                        .union(['shall', 'cannot', 'could', 'done', 'let', 'may' 'mayn',
                                       'might', 'must', 'need', 'ought', 'oughtn',
                                       'shall', 'would', 'br'])
        with open("data/keywords.json", "r") as read_file:
            self.keywords = json.load(read_file)

        self.processed_tweet = ""

        self.topics_cols =  ['Traffic',
       'Weather (Regular)', 'Weather (Extreme)', 'Crime', 'Events',
       'Lifestyle', 'Entertainment', 'Sports', 'Education', 'Politics',
       'City Hall types stories', 'State House types stories',
       'Courthouse types stories', 'Economy', 'Business', 'Stock Exchange',
       'Health', 'Science', 'Technology', 'Travel', 'Leisure', 'Obituaries',
       'Abortion', '2nd Amendment', 'Immigration', 'Police Brutality',
       'Terrorism', 'Race', 'Religion', 'Russian Sphere']



    def __str__(self):
        return pformat(vars(self), indent=4, width=1)



    def concat_text_list_to_text(self, text_list):
        if len(text_list) == 1:
            return text_list[0]
        elif len(text_list) > 1:
            return " ".join(text for text in text_list)
        else:
            return ""
   

    def remove_links(self, tweet):
        '''Takes a string and removes web links from it'''

        tweet = re.sub(r'http\S+', '', tweet) # remove http links
        tweet = re.sub(r'bit.ly/\S+', '', tweet) # rempve bitly links

        return tweet

    def remove_users(self, tweet):
        '''Takes a string and removes retweet and @user information'''
        tweet = re.sub('(RT\s@[A-Za-z]+[A-Za-z0-9-_]+)', '', tweet) # remove retweet
        tweet = re.sub('(@[A-Za-z]+[A-Za-z0-9-_]+)', '', tweet) # remove tweeted at
        return tweet


    def get_full_text(self):
        tmp = {}
        for c in ["Link Title", "Article content in the tweet", "Specific Hashtag"]:
            tmp[c] = self.concat_text_list_to_text(self.data[c])

        other_text_cols = ["Tweet content"]

        res =  " ".join(str(tmp[c]) for c in ["Link Title", "Article content in the tweet", "Specific Hashtag"])
        for c in other_text_cols:
            res = self.data[c] + " " + res
        return res

    def preprocess_tweets(self, pos_to_keep=None, return_str=True):
        """
            Preprocess document into normalised tokens.
        """
        stop_words=self.stop_words
        text = self.get_full_text()
        
        print("text:", text)
        
        text = self.remove_links(text)
        
        text = self.remove_users(text)
        


        # Tokenise into alphabetic tokens with minimum length of 3
        tokeniser = RegexpTokenizer(r'[A-Za-z]{3,}')
        tokens = tokeniser.tokenize(text)

        # Lowercase and tag words with POS tag
        tokens_lower = [token.lower() for token in tokens]
        pos_map = {'J': 'a', 'N': 'n', 'R': 'r', 'V': 'v'}
        pos_tags = pos_tag(tokens_lower)

        # Keep tokens with relevant pos
        if pos_to_keep is not None:
            pos_tags = [token for token in pos_tags if token[1][0] in pos_to_keep]

        # Lemmatise
        lemmatiser = WordNetLemmatizer()
        lemmas = [lemmatiser.lemmatize(t, pos=pos_map.get(p[0], 'v')) for t, p in pos_tags]

        # Remove stopwords
        keywords = [lemma for lemma in lemmas if lemma not in stop_words]
        if return_str:
            keywords = " ".join(k for k in keywords)

        self.processed_tweet = keywords
        return None


    def get_num_words(self, key_words):
        if not self.processed_tweet:
            self.preprocess_tweets()
        
        text = self.processed_tweet
        count = 0
        if (not text) or (not key_words):
            return count
        
        text_list = text.split(" ")
        keys_appearing = []
        for key in key_words:
            if key in text_list:
                count+=1
                keys_appearing.append(key)
                continue
        return count, keys_appearing

    def tweet_to_df(self):
        if not self.processed_tweet:
            self.preprocess_tweets()
        df_tweets = pd.DataFrame({"all_text_processed": [self.processed_tweet], "tweetid":[self.data["tweetid"]]})    

        return df_tweets


    def get_top_n_topics(self, n=5):
        topics_cols = self.topics_cols
        df_tweets = self.tweet_to_df()
        topics_dict = self.keywords

        for c in topics_cols:
            df_tweets[c], df_tweets[c+"_keywords"] = zip(*df_tweets["all_text_processed"].map(lambda text: self.get_num_words(topics_dict.get(c))))

        df_2 = df_tweets[topics_cols+["tweetid"]]

        x=df_2[topics_cols].T

        rslt = pd.DataFrame(np.zeros((0,n*2)), columns= ['top{}'.format(i+1) for i in range(n)] + ['score{}'.format(i+1) for i in range(n)] )
        for i in (x.columns):
            tmp = x.nlargest(n, i)
            df1row_score = pd.DataFrame(tmp[i].values.tolist(), index=['score{}'.format(i+1) for i in range(n)]).T
            df1row_index = pd.DataFrame(tmp.index.tolist(), index=['top{}'.format(i+1) for i in range(n)]).T
            df1row = pd.concat([df1row_index, df1row_score], axis=1)
            rslt = pd.concat([rslt, df1row], axis=0)
        
        rslt.reset_index(drop=True, inplace=True)
        # rslt = pd.concat([rslt, ], axis=1)

        return rslt, df_tweets[[c +"_keywords" for c in topics_cols]]



