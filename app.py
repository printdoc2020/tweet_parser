import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import json
import tweepy
from parse_raw_tweet import parse_raw_tweet 
import base64
import yaml

st.set_page_config(
	 page_title="Tweet Parser",
	 page_icon="random",
	 layout="wide",
	 initial_sidebar_state="expanded",
 )


def read_config():

	with open("config.yaml", 'r') as ymlfile:
		config = yaml.safe_load(ymlfile)

	## authenticate
	auth = tweepy.OAuthHandler(st.secrets['CONSUMER_KEY'], st.secrets['CONSUMER_SECRET'])
	auth.set_access_token(st.secrets['ACCESS_TOKEN'], st.secrets['ACCESS_SECRET'])
	api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)

	all_cols = config["all_cols"]
	return api, all_cols




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


st.title('Tweet Parser')
st.write('Last updated: May 14, 2021')

api, all_cols= read_config()

# id_of_tweet = st.text_input('crawl tweet id:', "")
tweet_url = st.text_input('Enter any tweet id, Ex: https://twitter.com/Quicktake/status/1392535793038671872', "")
# embed streamlit docs in a streamlit app




if tweet_url:

	html_template = f'<blockquote class="twitter-tweet"><a href="{tweet_url}"></a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>'

	id_of_tweet = tweet_url.split("/")[-1]
	try:
		raw_tweet = api.get_status(id_of_tweet, tweet_mode="extended")._json
	except:
		st.markdown('**Can not crawl the tweet. Please check on the tweet ID!**')
		raw_tweet = None
	if raw_tweet:
		tweet =  parse_raw_tweet(raw_tweet)
		data = tweet.data
		df = pd.DataFrame([data], columns=data.keys())

		data['Date'] = data['Date'] 
		data['Time'] = data['Time'] + " UTC"


		st.write(data)

		# num_links = data['# links']
		# for i in range(num_links):
		# 	st.



		top_n_topics_df, keywords_appearing_df = tweet.get_top_n_topics()
		st.write(top_n_topics_df)

		st.markdown(f"**All texts (tweet content, article content,...) after processing:** _{tweet.processed_tweet}_")

		st.write(keywords_appearing_df.T.sort_index())


		st.markdown("**Tweet ID:** " + data["tweetid"])

		components.html(html_template, height=600, width=None, scrolling=True)


		correct_topics = st.multiselect(
	     'Choose correct topic(s) for the tweet (the topics(s) below suggested by the dictionary)',
	     sorted(tweet.topics_cols),
	     [top_n_topics_df["top1"].values])


		for c in all_cols:
			if c not in df.columns:
				if c in correct_topics:
					df[c] = 1
				elif c in tweet.topics_cols:
					df[c] = 0
				else:
					df[c] = ""


		tmp_download_link = download_link(df.T, f'tweet_{id_of_tweet}.csv', 'Click HERE to download to file (can use Excel to open it)')
		st.markdown(tmp_download_link, unsafe_allow_html=True)



