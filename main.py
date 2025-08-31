"""
Creditation:
NASDAQ stock ticker from https://datahub.io/core/nasdaq-listings
"""

import re
import praw
import pandas as pd
import time
from datetime import datetime
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

def reddit_api():
	# Authenticate
	reddit = praw.Reddit(
    		client_id="l7QxHLU5G6LA0K5clnf8mA",
    		client_secret="vIB4EKvaMnqbbA9HFfswez110LhJLg",
    		user_agent="FINconnu",
	)
	return reddit

'''
def scrape_subreddit(reddit, sub_name, time_filter, num_posts):
	sub = reddit.subreddit(sub_name)
	# get all posts today:
	since = sub.top(time_filter=time_filter, limit=num_posts)
	# dataframe for all posts:
	ret = pd.DataFrame({
		"Title":[],
		"Karma":[],
		"Time":[],
		"Tags":[],
	})
	# for each, print info:
	for i, post in enumerate(since):
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

def get_tickers(title, valid_tickers):
	# custom set of invalid tickers:
	invalid_tickers = {"AI", "BULL", "BEAR", "LOSS", "GAIN", "CALL", "PUT"}
	# get all words which are valid tickers:
	possible_tickers = re.findall(r'\b[A-Z]{1,5}\b', title)
	tickers = [x for x in possible_tickers if x in valid_tickers and x not in invalid_tickers]
	# return all tickers which aren't empty:
	tickers = [x for x in tickers if x]
	return tickers

def token_sentiments(post, valid_tickers):
	# extract tickers from title:
	title = post["Title"]
	ticks = get_tickers(title, valid_tickers)
	# analyse title
	analyzer = SentimentIntensityAnalyzer()
	scores = analyzer.polarity_scores(title)
	sent = scores["pos"] 
	# weight by karma:
	sent *= post["Karma"]
	# return dictionaries with corresponding sentiment:
	ret = dict(zip(ticks, [sent for x in ticks]))
	return ret

'''

def scrape_since(reddit, subreddit, since):
	subreddit = reddit.subreddit(subreddit)
	# get all new reddit posts until one is past date:
	ret = []
	for post in subreddit.new(limit=None):
		# stop if out of range:
		if post.created_utc < since:
			break
		else:
			ret.append(post)
	#
	return ret

def get_tickers(post):
	# get any valid tickers in the post:
	words = post.title.split(" ")
	valid_tickers = pd.read_csv("nasdaq_listings.csv")["Symbol"]
	valid_tickers = set(valid_tickers)
	tickers = [x for x in words if x in valid_tickers]
	# handle tickers with $ in front
	tickers += [x for x in words if x and x[0] == "$" and x[1:] in valid_tickers]
	return tickers

def get_score(post):
	# get sentiment - either from tags or from title, whichever is more prominent:
	analyzer = SentimentIntensityAnalyzer()
	results = analyzer.polarity_scores(post.title)
	score = results["pos"] - results["neg"]
	flair = post.link_flair_text.split(" ")
	# logic to handle whether or not pos or negative:
	if abs(score) < 0.5:
		if "Gain" in flair:
			score = 0.5
		elif "Loss" in flair:
			score = -0.5
	# weight by karma, if any:
	if post.score:
		score *= post.score
	return score

def leaderboard(subreddit, since, interval, debug=False):
	''' takes name of subreddit, interval to scrape since and optional debug parameter, returns formatted leaderboard in descending order'''
	# get valid stock tickers:
	valid_tickers = pd.read_csv("nasdaq_listings.csv")["Symbol"]
	# common DataFrame to store results:
	df = pd.DataFrame({"stock": valid_tickers, "score": [0 for x in valid_tickers]})
	# loop continuously
	while True:
		reddit = reddit_api()
		scraped = scrape_since(reddit, subreddit, since)
		if debug:
			print(scraped)
		# get score for each, add to DataFrame:
		for post in scraped:
			tickers = get_tickers(post)
			score = get_score(post)
			for y in tickers:
				df["stock" == y] += score
		df = df.sort_values(by="score", ascending=False)
		print(df)
		# increment time by 1 interval:
		since += interval
		# wait until past that interval to repeat:
		while datetime.now() < datetime.utcfromtimestamp(since):
			time.sleep(1)
			if debug:
				print(datetime.utcfromtimestamp(since))


if __name__ == "__main__":
	ranks = leaderboard(
		"wallstreetbets", 
		since = int(time.mktime(time.strptime('2025-08-31 13:55:00', '%Y-%m-%d %H:%M:%S'))),
		interval = 60,
		debug=True
	)
