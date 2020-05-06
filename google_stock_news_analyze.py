
import requests

target = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
resp = requests.get(target)

from bs4 import BeautifulSoup
import bs4

soup = BeautifulSoup(resp.text, 'lxml')
table = soup.find('table', {'id': 'constituents'})

rows = list(table.find_all('tr'))

all_tickers = []
for row in rows[1:]:
    company = {}
    children = row.children
    children = [child for child in children if type(child) is bs4.element.Tag]
    company['ticker'] = children[0].get_text().strip()
    company['name'] = children[1].get_text()
    company['sector'] = children[3].get_text()
    company['quote_url'] = children[0].find('a')['href']
    all_tickers.append(company)
    
#for ticker in all_tickers:
#    if ticker['sector'] == 'Health Care':
#        print(ticker['ticker'], ' | ', ticker['name'])

all_health_care = [ ticker for ticker in all_tickers if ticker['sector'] == 'Health Care']
all_tech = [ ticker for ticker in all_tickers if ticker['sector'] == 'Information Technology']

search_target = "https://www.google.com/search?q={}+stock&safe=strict&tbm=nws&ei=Gb1VXfqNDc3UtQXFoL7oDQ&start={}&sa=N&ved=0ahUKEwi6_qel2IXkAhVNaq0KHUWQD90Q8tMDCF8&biw=1527&bih=739&dpr=1.1"

from bs4 import BeautifulSoup

def get_news_item(webpage_goog):
    target_div = 'g'
    soup = BeautifulSoup(webpage_goog, 'lxml')
    cards = soup.find_all('div', {'class': target_div}) #Returns a resultset
    #print('Found {} cards'.format(len(cards)))
    return list(cards)

def clean_google_url(dirty_url):
    return dirty_url.split('&sa')[0].split('q=')[1]

from nltk.sentiment.vader import SentimentIntensityAnalyzer

def get_polarity_score(text):
    sia = SentimentIntensityAnalyzer()
    return sia.polarity_scores(text)['compound']

    
from newspaper import Article, ArticleException
def get_link_title_from_card(list_cards):
    all_links = []
    for item in list_cards:
        single_news = {}
        grab = list(item.findChildren('a'))[0]
        url = clean_google_url(grab['href'])
        print("Scrapping actual news from {}".format(url))
        single_news['url'] = url
        try:
            article = Article(url)
            article.download()
            article.parse()
            single_news['headline'] = article.title
            single_news['news_page'] = article.text
            single_news['authour'] = article.authors
            single_news['keywords'] = article.keywords
            single_news['date'] = article.publish_date
            single_news['sentiment'] = get_polarity_score(article.text)
        except ArticleException as ae:
            print('Could not fetch article at {}'.format(url))
        all_links.append(single_news)
    return all_links


def fetch_via_proxy(url):
    import time
    from http_request_randomizer.requests.proxy.requestProxy import RequestProxy
    req_proxy = RequestProxy()
    request = req_proxy.generate_proxied_request(url)
    if request is not None:
        time.sleep(5)
        return request

import time
import datetime
import random
all_scraped = {}
list_slice = all_tickers
for company in list_slice:
    start = datetime.datetime.now()
    scrape = []
    ticker = company['ticker']
    for page in range(0, 100, 10):
        ok = False
        while not ok:
            resp = requests.get(search_target.format(ticker, page))
            if resp: ok = resp.ok
            #time.sleep(random.choice([1,2,3,4,5]))
        print('Scrapping headlines on page {} for {} on www.google.com'.format(int(page/10+1), ticker))
        scrape.extend(get_link_title_from_card(get_news_item(resp.text))) 
    all_scraped[ticker] = scrape
    percent_done = int((list_slice.index(company)+1)/len(list_slice) * 100)
    diff =   (datetime.datetime.now() - start).total_seconds()
    to_do = len(list_slice) - list_slice.index(company) + 1
    to_go = (diff * to_do)/60
    print("We are {}% completed. {} minutes to go".format(round(percent_done, 2), to_go))


import pickle
with open('all_scraped.dat') as file:
    pickle.dump(all_scraped, file)

#mmm = all_scraped['MMM']
#neg_news_mmm = [news for news in mmm if news['sentiment'] < 0]






