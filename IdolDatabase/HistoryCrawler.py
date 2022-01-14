import re
import requests
import time
from bs4 import BeautifulSoup
from operator import itemgetter
from datetime import datetime, timezone

class HistoryCrawlerException(Exception): pass
class HistoryCrawler:
	endpoint_url_root = "https://allstars.kirara.ca{:s}"
	endpoint_url_page = "https://allstars.kirara.ca/{{:locale}}/history/{:d}"

	def __init__(self):
		pass
		
	def _request_and_parse_page(self, url):
		locales = ['en', 'jp']
		
		result = []
		next_page_url = False
		
		r = requests.get(url, headers={
			'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0',
			# 'Referer'    : 'https://allstars.kirara.ca/en/history/',
		})
		print("Crawling page url", url)
		
		if r.status_code != 200:
			print("Request failed", r.status_code)
			print(r.text)
			raise HistoryCrawlerException("Request failed")
		
		
		event_info_pattern = re.compile(r"(.*) Event: (.*)")
		
		soup = BeautifulSoup(r.content, 'html.parser')
		
		next_page = soup.select_one('.page-item:last-child a.page-link')
		if next_page and ('Next' in next_page.decode_contents()):
			next_page_url = HistoryCrawler.endpoint_url_root.format(next_page['href'])
			print("Found next page url", next_page_url)
		else:
			print("Could not find next page url, this must be the last page.")
			
		news = soup.select('div.kars-news-header > .item')
		for n in news:
			header = n.select_one('h1')
			if not header:
				continue
				
			timestamps = n.select('h2 span.kars-data-ts')
			if len(timestamps) != 2:
				continue
			
			title = header.decode_contents().strip()
			if 'Event' not in title:
				continue
				
			event_info = event_info_pattern.findall(title)
			# print(event_info)
			
			if not event_info or len(event_info[0]) != 2:
				print("Could not parse event info", title)
				continue
				
			event_type = event_info[0][0]
			event_title = event_info[0][1]
			
			if not event_type:
				print("Could not retrieve event type")
				continue
			
			if not event_title:
				print("Could not retrieve event title")
				continue
			
			try:
				start_ts = int(float(timestamps[0]['data-ts']))
				start = datetime.utcfromtimestamp(start_ts)
				
				end_ts = int(float(timestamps[1]['data-ts']))
				end = datetime.utcfromtimestamp(end_ts)
			except:
				print("Could not parse event timestamps")
				continue
				
			result.append((
				hash(event_title),
				{
					'title' : event_title,
					'type'  : event_type,
					'start' : start,
					'end'   : end,
				}
			))
			
		return result, next_page_url
			
	def crawl_events(self, known_events = []):
		events = []
		next_page_url = HistoryCrawler.endpoint_url_page_id.format(1)
		while True:
			event_data, next_page_url = self._request_and_parse_page(next_page_url)
			events.extend(event_data)
			
			if any(x['title'] in known_events for _, x in event_data):
				print("Found a known event in the list, no need to continue crawling")
				break
			
			if next_page_url == False:
				break
			time.sleep(0.1)
		
		events = [x for _, x in dict(events).items()]
		sorted_events = list(sorted(events, key=itemgetter('start')))
		return sorted_events

##################################

if __name__ == "__main__":
	hc = HistoryCrawler()
	known_events = ['Japanese-Style Thanksgiving Day']
	hc.crawl_events(known_events);
