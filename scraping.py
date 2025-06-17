# imports:
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

# classes / funcs:

def brave_driver(brave_path="/usr/bin/brave-browser", wait=5):
	# create and return brave webdriver:
	options = Options()
	options.binary_location = brave_path
	brave = webdriver.Chrome(options=options)
	brave.implicitly_wait(wait)
	return brave

def access_reddit(driver):
	# go to site:
	driver.get("https://reddit.com/")
	# --- if blocked, make account w/ temp email ---
	# otherwise, nothing to do

def scrape_sub(driver, url, until="day"):
	# scrape all posts until given point - select time here:
	url += f"?t={until}"
	# go to subreddit:
	driver.get(url)
	# scrape all the posts - get all, scroll, refresh until no new elements:
	old = driver.find_elements(By.TAG_NAME, "article")
	new = []
	ret = old
	while old != new:
		# scroll down fully:
		driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
		time.sleep(5)
		# update and merge w/ existing posts
		old = new
		ret += old 
		new = driver.find_elements(By.TAG_NAME, "article")
	# return all posts:
	return ret	

# testing:

if __name__ == "__main__":
	try:
		# create driver:
		brave = brave_driver(wait=10)
		# scrape the subreddit:
		posts = scrape_sub(brave, "https://reddit.com/r/wallstreetbets/") 
		print(posts)

	# in case of Crtl+C:
	finally:
		brave.quit()
