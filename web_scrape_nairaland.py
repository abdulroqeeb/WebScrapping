#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jul 28 11:55:00 2019

@author: abdulroqeeb
"""


import requests	
from bs4 import BeautifulSoup

target = 'https://www.nairaland.com/'
resp = requests.get(target)

if resp.ok: text = resp.text

concern_td = 'featured w'

soup = BeautifulSoup(text, 'lxml')
found = soup.find('td', {'class': concern_td })

headlines = list(found.find_all('a'))

#Alternative way, not recommended
headlines_2 = []
for item in found.find_all('a'):
	headlines_2.append(item)

headlines_dict = { headline['href'] : headline.text for headline in headlines}

import random
one_headline = random.choice(list(headlines_dict.keys())) 


def clean_url(url):
	spl = url.split('/')
	new_url = '/'.join(spl[:5])
	return new_url

'''
Scraping comments from the pages
'''

def body_util(webpage):
	concern_td = 'l w pd'
	soup = BeautifulSoup(webpage, 'lxml')
	found = soup.find_all('td', {'class': concern_td })
	return [item.get_text() for item in found]

def get_body_from_webpage(url):
	resultlist = []
	page = 0
	cont = True
	while cont:
		url = clean_url(url) + '/' + str(page)
		resp = requests.get(url)
		page += 1
		print('Getting page {} from {}'.format(page, url))
		result = body_util(resp.text)
		if resp.url != url:
			break
		resultlist.extend(result)
	return resultlist


all_scraped = {}
for item in headlines_dict.keys():
	scraped = get_body_from_webpage(item)
	percent_done = (list(headlines_dict.keys()).index(item)+1) / len(headlines_dict) * 100
	print("We are {}% done".format(round(percent_done,2)))
	all_scraped[item] = scraped

import pickle
file = open('website.dat', 'wb')
pickle.dump(all_scraped, file)
file.close()

#Preferred alternative method to read and write.
with open('website.dat', 'wb') as file:
	pickle.dump(all_scraped, file)

'''
End of Data gathering and Beginning of manipulation
'''

import pickle
with open('website.dat', 'rb') as file:
	all_scraped = pickle.load(file)


#Run the next two lines of code from the python interpreter (cmd or terminal on mac)
#import nltk
#nltk.download()

from nltk.sentiment.vader import SentimentIntensityAnalyzer
sia = SentimentIntensityAnalyzer()

negatives = []
for item in all_scraped.values():
	negatives.extend([post for post in item if sia.polarity_scores(post)['neg'] > 0.7])
	