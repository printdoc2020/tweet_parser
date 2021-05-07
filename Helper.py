import glob
import json
import random
from pprint import pprint
import requests
from bs4 import BeautifulSoup
from urllib.parse import  unquote
import re
from os.path import join as os_join
import os

class Helper:
    data_path = "/data/"
    out_path = "/data/output/"
    
    def __init__(self):
        pass

    @staticmethod
    def expandURL(link):
        res = link
        try:
            res =  requests.head(link, headers={"User-Agent":"Mozilla/5.0"}, allow_redirects=True).url
        except:
            print("expandURL(link)", link)
        finally:
            return res


    @staticmethod
    def get_a_raw_tweet_by_id(tweetid, file_name = None):
        if file_name:
            try:
                file = glob.glob(Helper.data_path +  file_name + "*.json")[0]
            except:
                file = glob.glob(Helper.data_path +  file_name.lower() + "*.json")[0]

            with open(file) as f:
                data = json.load(f)
            for raw_tweet in data:
                if raw_tweet["id"] == int(tweetid):
                    return raw_tweet

        else:
            file_list = glob.glob(Helper.data_path + "*.json")
            for i, file in enumerate(file_list):
                with open(file) as f:
                    data = json.load(f)
                for raw_tweet in data:
                    if raw_tweet["id_str"] == tweetid:
                        return raw_tweet

        return None

    @staticmethod
    def get_a_raw_tweet_by_index(file_index=-1, tweet_index=-1):
        file_list = glob.glob(Helper.data_path + "*.json")
        num_files = len(file_list)

        if file_index == -1:
           file_index_new = random.randint(0, num_files - 1)

        with open(file_list[file_index_new]) as f:
            data = json.load(f)

        if tweet_index == -1:
            tweet_index_new = random.randint(0, len(data) - 1)
        if file_index == -1 or tweet_index == -1:
            print(f"get_a_random_raw_tweet, with file_index={tweet_index_new}, tweet_index={file_index_new}")
        return data[tweet_index_new]

    @staticmethod
    def get_a_random_raw_tweet():
        return Helper.get_a_raw_tweet_by_index()


    @staticmethod
    def get_tweet_url_from_raw_tweet(tweet):
        screen_name = tweet["user"]["screen_name"]

        tweet_url =  "https://twitter.com/" + screen_name + "/status/" + tweet["id_str"]
        return tweet_url


    @staticmethod
    def get_all_raw_tweets_as_list(flatten = False):
        res = list()
        file_list = glob.glob(Helper.data_path + "*.json")
        for file in file_list:
            with open(file) as f:
                data = json.load(f)
            if flatten:
                res.extend(data)
            else:
                res.append(data)
        return res

    @staticmethod
    def get_all_raw_tweets_as_json(over_write=False, output_path=None):
        if output_path:
            output_path = Helper.out_path
        res = dict()
        file_list = glob.glob(Helper.data_path + "*.json")

        if over_write == False:
            print(f"#files total {len(file_list)} files")
            file_names = os.listdir(output_path)
            try:
                file_names.remove(".DS_Store")
            except:
                pass
            print(f"already had {len(file_names)} files")
            remaining_files = [f for f in file_list if f.rsplit("/", 1)[-1] not in set(file_names)]
            print("#remaining files", len(remaining_files))
            file_list = remaining_files

        for file in file_list:
            with open(file) as f:
                data = json.load(f)
            res[file.rsplit("/",1)[-1]] = data


        return res

    @staticmethod
    def get_all_raw_tweets_from_a_list_as_json(file_names):
        res = dict()
        file_list = glob.glob(Helper.data_path + "*.json")

        print(f"#files total {len(file_list)} files")


        remaining_files = [f for f in file_list if f.rsplit("/", 1)[-1] in set(file_names)]
        print("Need to parse", len(remaining_files))

        file_list = remaining_files

        for file in file_list:
            with open(file) as f:
                data = json.load(f)
            res[file.rsplit("/", 1)[-1]] = data

        return res





    @staticmethod
    def get_raw_tweets_by_screeen_name(screen_name, tweetid=None):
        file = glob.glob(Helper.data_path + screen_name + "*.json")[0]
        with open(file) as f:
            raw_tweet_list = json.load(f)

        if tweetid:
            for raw_tweet in raw_tweet_list:
                if raw_tweet["id_str"] == tweetid:
                    return raw_tweet
        else:
            return raw_tweet_list


    @staticmethod
    def get_redict_url(raw_url):
        resp = requests.get(raw_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=(5, 20))
        ## Time out: senconds. Read more at https://requests.kennethreitz.org/en/master/user/advanced/#timeouts

        ## check num of http links
        if resp.url.count("http") > 1:
            url = unquote('http' + resp.url.split('http')[-1])
        else:
            url = raw_url
        return url


    @staticmethod
    def extract_embedded_url_content(website, url):

        """
        https://stackoverflow.com/questions/22318095/get-meta-description-from-external-website
        """
        res = dict()
        res["link_works"] = 0

        if not url:
            return res


        # print("raw url:", url)
        resp = requests.get(url, headers={"User-Agent":"Mozilla/5.0"})


        ## check num of http links
        if resp.url.count("http") > 1:
            url = unquote('http' + resp.url.split('http')[-1])

        # print("url:", url)
        # print("resp.status_code", resp.status_code)

        if resp.status_code == 200:
            soup = BeautifulSoup(resp.content, "html.parser")
            res["link_works"] = 1
        else:
            return res

        description_selectors = [
            {'name': 'twitter:description'},
            {'name': 'twitter:text:description'},
            {"name": "og:description"},
            {"property": "og:description"},
            {"name": "description"},
            {"property": "description"}
        ]
        final_description = ''
        for selector in description_selectors:
            description_tag = soup.find("meta", selector)
            if description_tag and description_tag.get('content'):
                final_description = description_tag['content']
                break

        title_selectors = [
            {'name': 'twitter:title'},
            {'name': 'twitter:text:title'},
            {"name": "og:title"},
            {"property": "og:title"},
            {"name": "title"},
            {"property": "title"}
        ]
        final_title = ''
        for selector in title_selectors:
            title_tag = soup.find("meta", selector)
            if title_tag and title_tag.get('content'):
                final_title = title_tag['content']
                break

        image_selectors = [
            {'name': 'twitter:image'},
            {"name": "og:image"}
        ]
        final_image = ''
        for selector in image_selectors:
            image_tag = soup.find("meta", selector)
            if image_tag and image_tag.get('content'):
                final_image = image_tag['content']
                break

        twitter_card = soup.find('meta', {'name': 'twitter:card'})


        res["have_twitter_card"] = twitter_card is not None
        res["title"] =  final_title
        res["description"] = final_description
        res["image"] = final_image
        res["url"] = resp.url

        res["own_website"] = Helper.check_a_url_in_website(website, url)

        return res


    @staticmethod
    def print_raw_tweet_list(tweet_list):
        for tweet in tweet_list:
            print(Helper.get_tweet_url_from_raw_tweet(tweet))
            pprint(tweet)
            print("\n====\n")

    @staticmethod
    def get_specific_clean_tweets(key, value, clean_tweet_list, operator="equal", max_res = 10):
        """
            find tweet which has tweet[key] == value
        """
        res = list()
        for tweet in clean_tweet_list:
            if operator == "equal":
                if tweet.data[key] == value:
                    res.append(tweet)
            elif operator == "equal_or_greater":
                if tweet.data[key] >= value:
                    res.append(tweet)
            elif  operator == "equal_or_smaller":
                if tweet.data[key] <= value:
                    res.append(tweet)

            if len(res) > max_res:
                break

        return res

    @staticmethod
    def check_a_url_in_website(website, a_url):


        if website is None:
            return 0
        url = Helper.expandURL(a_url)

        if website.lower() in url.lower():
            return 1
        else:
            return 0


    @staticmethod
    def check_website_in_url_list(website, url_list):

        if website is None:
            return 0


        url_parse = re.compile(r"https?://(www\.)?")

        url_full_list = list(map(Helper.expandURL, url_list))
        # print("raw website", website)
        # print("url_full_list", url_full_list)

        website = url_parse.sub('', website).strip().split("/")[0].strip('/')

        # print("clean website", website)

        for url in (url_full_list):
            if website in url:
                return 1
        return 0


    @staticmethod
    def write_to_json(obj, file_out_path, file_name, adding_extension):
        if adding_extension:
            file_path_full = os_join(file_out_path, file_name) + ".json"
        else:
            file_path_full = os_join(file_out_path, file_name)

        with open(file_path_full, 'w') as f:
            json.dump(obj, f)


    @staticmethod
    def get_tweet_from_twitter_url(twitter_url):
        """
        input: Twitter URL, ex: "https://twitter.com/SuffolkJournal/status/1328423913035075584"
        output: tweet 
        """
        pass
