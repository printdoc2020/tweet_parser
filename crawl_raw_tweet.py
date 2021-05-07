import tweepy
import json
import csv
import time
from pprint import pprint
import pandas as pd
from collections import Counter
from os.path import join as os_join
import numpy as np
from tqdm import tqdm

def authenticate():
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
    api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)
    return api


## TODO: add to config file
ACCESS_TOKEN = '41080440-qjZ1Jl4Ua61IXtvN4WSxUnm3RoxEaBHYGkOWLqQQO'
ACCESS_SECRET = 'aCKVeUDUIuxp9ZpFPmZWpbdOfq4N1LDKSQohTUsIhngIh'
CONSUMER_KEY = '75bNvkIXnOFPKqU44O9ClIjNR'
CONSUMER_SECRET = '89Es022ydnPadYRBm9F7lC8NaW1XhgmT7xjbV0UQhs673Si2iN'


##
if __name__ == '__main__':
	api = authenticate()

	# https://twitter.com/Rita95366602/status/1243582555980541954
	id_of_tweet = 1243582555980541954
	raw_tweet = api.get_status(id_of_tweet, tweet_mode="extended")._json
	print(raw_tweet)

