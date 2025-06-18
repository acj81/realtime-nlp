"""
Creditation:
stock ticker CSV from https://www.nasdaq.com/market-activity/stocks/screener
"""


import praw
import pandas as pd
import textblob as txb

def reddit_api():
	# Authenticate
	reddit = praw.Reddit(
    		client_id="l7QxHLU5G6LA0K5clnf8mA",
    		client_secret="vIB4EKvaMnqbbA9HFfswez110LhJLg",
    		user_agent="FINconnu",
	)
	return reddit

def scrape_subreddit(reddit, sub_name):
	sub = reddit.subreddit(sub_name)
	# get all posts today:
	today = sub.top(time_filter="day")
	# dataframe for all posts:
	ret = pd.DataFrame({
		"Title":[],
		"Karma":[],
		"Time":[],
		"Tags":[],
	})
	# for each, print info:
	for i, post in enumerate(today):
		# format into series, add to DataFrame:
		post_frame = pd.DataFrame({
			"Title":[post.title],
			"Karma":[post.score],
			"Time":[post.created_utc],
			"Tags":[post.link_flair_text],
		})
		ret = pd.concat([ret, post_frame], ignore_index=True)
	# 
	return ret

def token_sentiments(title):
	# extract tickers:
	stock_tickers = pd.read_csv("nasdaq_screener_1750271204515.csv")
	ticks = [x for x in title.split(" ") if x in str(stock_tickers["Symbol"])]
	# analyse title
	sent = txb.TextBlob(title)
	# return dictionaries with corresponding sentiment:
	ret = dict(zip(ticks, [sent for x in ticks]))
	return ret

if __name__ == "__main__":
	# testing - get top posts from wallstreetbets
	reddit = reddit_api()
	scraped = scrape_subreddit(reddit, "wallstreetbets")
	print(scraped)
	# do sent. analysis on each:
	sents = [token_sentiments(x) for x in scraped["Title"]]
	print(sents)
# 
