import re
import requests
from bs4 import BeautifulSoup

class Crawler:
	root_url = "https://allstars.kirara.ca{}"
	news_list_url = "https://allstars.kirara.ca/en/news/"
	
		
	def _request_page(self, url):
		r = requests.get(url, headers={
			'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
			# 'Referer'    : 'https://allstars.kirara.ca/en/history/',
		})
		
		if r.status_code != 200:
			print("Request failed", r.status_code)
			print(r.text)
			raise Exception("Request failed")
		
		return r.content
		
	def _parse_news_list_page(self, html_data):
		soup = BeautifulSoup(html_data, 'html.parser')
		if not soup:
			return False
		
		result = []
		next_page_url = False
		
		next_page = soup.select_one('a.btn.btn-primary[href*="/en/news/?before="]')
		if next_page and ('More' in next_page.decode_contents()):
			href = next_page['href']
			before = re.findall(r'before\=(\d*)', href)

			if before:
				before = int(before[0])
				before += 7 * 24 * 3600
				href = f'/en/news/?before={before}'
			
			next_page_url = Crawler.root_url.format(href)
			print("Found next page url", next_page_url)
		else:
			print("Could not find next page url, this must be the last page.")
			
		title_needles = ['Big Live', 'Mega Live', 'School Idol Festival']
		
		news = soup.select('.kars-news-header a[href*="/en/news"]')
		for n in news:
			title = n.decode_contents().strip()
			if not any(x in title for x in title_needles):
				continue
			
			title = title.replace('Join in the', '').strip()
			
			result.append({
				'title' : title,
				'url'   : Crawler.root_url.format(n['href']),
			})
		
		return result, next_page_url
		
	def _parse_sbl_news_page(self, html_data):
		soup = BeautifulSoup(html_data, 'html.parser')
		if not soup:
			return False
			
		article = soup.select_one('.kars-news-container article')
		if not article:
			raise Exception("Article not found what?")
		
		current_events = []
		next_events = []
		parse_event_names = 0
		
		article_body = article.decode_contents().strip().split('\n')
		for line in article_body:
			line = line.strip()
			if not line:
				continue
			
			# print(line)
			
			if parse_event_names != 0:
				name = re.findall(r'・(.*)', line)
				# print("Regex", name)
				
				if parse_event_names == 1:
					if not name:
						parse_event_names = 0
						continue
					
					current_events.extend(name)
					
				elif parse_event_names == 2:
					if not name:
						break
					
					next_events.extend(name)
				
				continue
			
			if 'Currently, school idols that were rewards' in line:
				# print("DIIIIIIIIIIIIIIIIIIIIING!")
				parse_event_names = 1
				continue
				
			elif 'next Big Live' in line:
				# print("DOOOOOOOOOOOOOOOOOOOOOOONG!")
				parse_event_names = 2
				continue
		
		return current_events, next_events
		
	def _remove_duplicates(self, events):
		output = []
		seen = set()
		for d in events:
			t = hash(d['title'])
			if t not in seen:
				seen.add(t)
				output.append(d)
		return output
	
	def crawl(self):
		sbl_news = []
		next_page_url = Crawler.news_list_url
		while True:
			print("Crawling", next_page_url)
			
			html_data = self._request_page(next_page_url)
			result, next_page_url = self._parse_news_list_page(html_data)
			
			sbl_news.extend(result)
			
			if next_page_url == False:
				break
		
		sbl_news = self._remove_duplicates(reversed(sbl_news))
		print(sbl_news)
		
		for news in sbl_news:
			print("Parsing news", news['title'], news['url'])
			html_data = self._request_page(news['url'])
			news['current_events'], news['next_events'] = self._parse_sbl_news_page(html_data)
			
		print(sbl_news)
			

crawly = Crawler()
crawly.crawl()

