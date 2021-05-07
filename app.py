import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import tweepy
from parse_raw_tweet import parse_raw_tweet 
import base64

st.set_page_config(
	 page_title="Tweet Parser",
	 page_icon="random",
	 layout="wide",
	 initial_sidebar_state="expanded",
 )


def read_config():
	## TODO: add to config file
	ACCESS_TOKEN = '41080440-qjZ1Jl4Ua61IXtvN4WSxUnm3RoxEaBHYGkOWLqQQO'
	ACCESS_SECRET = 'aCKVeUDUIuxp9ZpFPmZWpbdOfq4N1LDKSQohTUsIhngIh'
	CONSUMER_KEY = '75bNvkIXnOFPKqU44O9ClIjNR'
	CONSUMER_SECRET = '89Es022ydnPadYRBm9F7lC8NaW1XhgmT7xjbV0UQhs673Si2iN'

	## authenticate
	auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
	auth.set_access_token(ACCESS_TOKEN, ACCESS_SECRET)
	api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)

	return api




def download_link(object_to_download, download_filename, download_link_text):
	"""
	Generates a link to download the given object_to_download.

	object_to_download (str, pd.DataFrame):  The object to be downloaded.
	download_filename (str): filename and extension of file. e.g. mydata.csv, some_txt_output.txt
	download_link_text (str): Text to display for download link.

	Examples:
	download_link(YOUR_DF, 'YOUR_DF.csv', 'Click here to download data!')
	download_link(YOUR_STRING, 'YOUR_STRING.txt', 'Click here to download your text!')

	"""
	if isinstance(object_to_download,pd.DataFrame):
		object_to_download = object_to_download.to_csv(index=True, header=False)

	# some strings <-> bytes conversions necessary here
	b64 = base64.b64encode(object_to_download.encode()).decode()

	return f'<a href="data:file/txt;base64,{b64}" download="{download_filename}">{download_link_text}</a>'



all_cols = ["Variables",
"Date",
"Time",
"Type",
"Hashtag 0/1",
"Hashtag #",
"Specific Hashtag",
"0/1 @",
"# @",
"Specific @",
"Tweet content",
"Link Title",
"Article Content in the Tweet",
"Link",
"Link 0/1",
"# links",
"link works",
"link to news website",
"Website Type",
"Social Media Type",
"Retweeted/Quoted @",
"Illustration",
"Illustration Type",
"Hashtag game",
"News phrase",
"Sensational phrase",
"Local",
"Regional",
"National",
"International",
"Traffic",
"Weather regular",
"Weather extreme",
"Crime",
"Events",
"Lifestyle",
"Entertainment",
"Sports",
"Education",
"Politics",
"City hall",
"Statehouse",
"Courthouse",
"Economy",
"Business",
"Stock Exchange",
"Health",
"Science",
"Technology",
"Travel",
"Leisure",
"Obituaries",
"Abortion",
"2nd Amenments",
"Immigration",
"Police brutality",
"Terrorism",
"Race",
"Gender",
"Religion",
"Russian Sphere",
"Discredit institutions",
"Discredit media",
"Unclear",
"Filler",
"Other topic",
"Informative",
"Fearmongering",
"Provocative",
"Reflexive portrayal"]





st.title('Tweet Parser')
st.write('Last updated: May 7, 2021')

api = read_config()
id_of_tweet = st.text_input('crawl tweet id:', "")
st.markdown('Enter **any** tweet id, for example: _"https://twitter.com/thetech/status/1370087554901553152"_ or simply _"1370087554901553152"_')

if id_of_tweet:

	id_of_tweet = id_of_tweet.split("/")[-1]

	raw_tweet = api.get_status(id_of_tweet, tweet_mode="extended")._json
	tweet =  parse_raw_tweet(raw_tweet)
	data = tweet.data
	df = pd.DataFrame([data], columns=data.keys())

	st.write(data)

	top_n_topics_df, keywords_appearing_df = tweet.get_top_n_topics()
	st.write(top_n_topics_df)

	st.markdown(f"**All texts (tweet content, article content,...) after processing:** _{tweet.processed_tweet}_")

	st.write(keywords_appearing_df.T)


	st.markdown("**Tweet ID:** " + data["tweetid"])

	for c in all_cols:
		if c not in df.columns:
			if c in top_n_topics_df["top1"].values:
				df[c] = 1
			elif c in tweet.topics_cols:
				df[c] = 0
			else:
				df[c] = ""


	tmp_download_link = download_link(df.T, f'tweet_{id_of_tweet}.csv', 'Click here to download the file')
	st.markdown(tmp_download_link, unsafe_allow_html=True)



