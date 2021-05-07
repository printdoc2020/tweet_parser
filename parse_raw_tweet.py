import pandas as pd
import numpy as np
import json
from pprint import pprint
import glob
from datetime import datetime
import unicodedata
import time
from tqdm import tqdm
import multiprocessing as mp


from Helper import Helper
from Tweet import Tweet
import re

NO_TEXT = ""


def parse_raw_tweet(raw_tweet, num=-1):
    # pprint(x)

    tweet = Tweet()

    tweet.data["Variables"] = num

    created_at = datetime.strptime(raw_tweet["created_at"], '%a %b %d %H:%M:%S +0000 %Y')
    tweet.data["Date"] = created_at.date().strftime("%B %d %Y")
    tweet.data["Time"] = created_at.time().strftime("%H:%M:%S")

    retweet_text = ""
    quote_tweet_text = ""
    original_tweet_text = raw_tweet["full_text"]

    try:
        retweet_text = raw_tweet["retweeted_status"]["full_text"]

        if retweet_text:
            tweet.data["Type"] = Tweet.tweet_type["retweet"]
    except:
        try:
            quote_tweet_text = raw_tweet["quoted_status"]["full_text"]
            if quote_tweet_text:
                tweet.data["Type"] = Tweet.tweet_type["quotetweet"]
        except:
            tweet.data["Type"] = Tweet.tweet_type["original_tweet"]

    raw_hashtags = raw_tweet["entities"]['hashtags']
    num_hashtags = len(raw_hashtags)
    tweet.data["Hashtag 0/1"] = 1 if num_hashtags >= 1 else 0
    tweet.data["Hashtag #"] = num_hashtags
    tweet.data["Specific Hashtag"] = ["#" + hashtag["text"] for hashtag in raw_hashtags]

    raw_user_mentions = raw_tweet["entities"]["user_mentions"]
    tweet.data["0/1 @"] = 1 if len(raw_user_mentions) >= 1 else 0
    tweet.data["# @"] = len(raw_user_mentions)
    tweet.data["Specific @"] = ["@" + mention["screen_name"] for mention in
                                raw_user_mentions]  ## Should we remove duplicates???: No need

    ## If a retweet, quotetweet, how to define this field???: put retweet into original tweets
    text_len = raw_tweet["display_text_range"][-1]
    if (tweet.data["Type"] == Tweet.tweet_type["original_tweet"]):
        tweet.data["Tweet content"] = unicodedata.normalize("NFKD", original_tweet_text[:text_len])
    elif (tweet.data["Type"] == Tweet.tweet_type["quotetweet"]):
        tweet.data["Tweet content"] = unicodedata.normalize("NFKD", original_tweet_text[:text_len])

        len_quotetweet_text = raw_tweet["quoted_status"]["display_text_range"][-1]
        tweet.data["quotetweet_text"] = unicodedata.normalize("NFKD", quote_tweet_text[:len_quotetweet_text])
    elif ((tweet.data["Type"] == Tweet.tweet_type["retweet"])):
        len_retweet_text = raw_tweet["retweeted_status"]["display_text_range"][-1]
        tweet.data["Tweet content"] = unicodedata.normalize("NFKD", retweet_text[:len_retweet_text])  ### How to fill in this???: assign to retweet
    else:
        tweet.data["Tweet content"] = NO_TEXT  ## default

    ### Should replace "twitter shorten url"  by "display url"???: No need

    ## Own Website


    try:
        own_website_urls = raw_tweet["user"]["entities"]["url"]["urls"]
        if len(own_website_urls) > 1:
            print("CHECK!!! --- own_website_urls>1", own_website_urls)
        own_website = own_website_urls[0]["expanded_url"]

        url_parse = re.compile(r"https?://(www\.)?")
        own_website = url_parse.sub('', own_website).strip().split("/")[0].strip('/')
    except:
        own_website = None

    ## Article content in the tweet
    raw_urls = raw_tweet["entities"]["urls"]
    url_list = []

    if raw_urls:
        if tweet.data["Type"] == Tweet.tweet_type["quotetweet"]:
            if len(raw_urls) >= 1:
                raw_urls = raw_urls[:-1]

        url_list = [url["expanded_url"] for url in raw_urls]

        tweet.data["Link 0/1"] = 1 if len(raw_urls) >= 1 else 0
        tweet.data["# links"] = len(raw_urls)

        data_from_url_list = [Helper.extract_embedded_url_content(own_website, url) for url in url_list]

        tweet.data["Link"] = []
        tweet.data["Link Title"] = []
        tweet.data["Article content in the tweet"] = []
        tweet.data["link works"] = []
        tweet.data["link to own news website"] = []
        tweet.data["Website Type"] = []
        tweet.data["Social Media Type"] = []

        for data_from_url in data_from_url_list:

            tweet.data["Website Type"].append(-1)  ### Do later TODO
            if data_from_url.get("url"):
                for media_type in Tweet.social_media_type.keys():
                    if media_type in data_from_url.get("url"):
                        tweet.data["Social Media Type"].append(Tweet.social_media_type[media_type])
                        break
                else:
                    tweet.data["Social Media Type"].append(Tweet.social_media_type["other"])
            else:
                tweet.data["Social Media Type"].append(Tweet.social_media_type["none"])



            if data_from_url.get("link_works"):
                tweet.data["Link"].append(data_from_url.get("url"))

                tweet.data["Link Title"].append(data_from_url["title"])
                tweet.data["Article content in the tweet"].append(data_from_url["description"])
                tweet.data["link works"].append(1)
                tweet.data["link to own news website"].append(data_from_url["own_website"])
                ### need image???
            else:
                tweet.data["Link"].append(data_from_url.get("url"))
                tweet.data["Link Title"].append(NO_TEXT)
                tweet.data["Article content in the tweet"].append(NO_TEXT)
                tweet.data["link works"].append(0)
                tweet.data["link to own news website"].append(-1)

    else:
        tweet.data["Link 0/1"] = 0
        tweet.data["# links"] = 0
        tweet.data["Link"] = [NO_TEXT]
        tweet.data["Link Title"] = [NO_TEXT]
        tweet.data["Article content in the tweet"] = [NO_TEXT]
        tweet.data["link works"] = []
        tweet.data["link to own news website"] = []



    if tweet.data["Type"] == Tweet.tweet_type["quotetweet"]:
        tweet.data["Retweeted/Quoted @"] = "@" + raw_tweet["quoted_status"]["user"]["screen_name"]

    elif tweet.data["Type"] == Tweet.tweet_type["retweet"]:
        tweet.data["Retweeted/Quoted @"] = "@" + raw_tweet["retweeted_status"]["user"]["screen_name"]
    else:
        tweet.data["Retweeted/Quoted @"] = None

    try:
        type = raw_tweet["extended_entities"]["media"][0]["type"]
        if type == "photo":
            tweet.data["Illustration Type"] = Tweet.illustration_type["image"]
        elif type == "animated_gif":
            tweet.data["Illustration Type"] = Tweet.illustration_type["gif"]
        elif type == "video":
            tweet.data["Illustration Type"] = Tweet.illustration_type["video"]
        else:
            tweet.data["Illustration Type"] = Tweet.illustration_type["other"]

        tweet.data["Illustration"] = 1
        tweet.data["Num Illustrations"] = len(raw_tweet["extended_entities"]["media"])
    except:
        tweet.data["Illustration Type"] = Tweet.illustration_type["none"]
        tweet.data["Illustration"] = 0
        tweet.data["Num Illustrations"] = 0

    tweet.data["tweetid"] = Helper.get_tweet_url_from_raw_tweet(raw_tweet)

    return tweet


def parse_raw_tweet_for_1_account(data):
    file_name, raw_tweet_list = (*data,)

    res = list()
    for i, raw_tweet in enumerate(raw_tweet_list):
        # print(i, Helper.get_tweet_url_from_raw_tweet(raw_tweet))
        clean_tweet = parse_raw_tweet(raw_tweet, i + 1)
        res.append(clean_tweet.data)

    Helper.write_to_json(res, Helper.out_path, file_name, False)
    print("Done", file_name)










