import re
import requests
import time
from bs4 import BeautifulSoup
from operator import itemgetter
from datetime import datetime, timezone
from collections import defaultdict

from .Config import Config

class HistoryCrawlerException(Exception): pass
class HistoryCrawler:
	endpoint_url_root = "https://allstars.kirara.ca{:s}"
	endpoint_url_page = "https://allstars.kirara.ca/{{:s}}/history/{:d}"

	def __init__(self):
		pass
	
	def _parse_page(self, html_data):
		soup = BeautifulSoup(html_data, 'html.parser')
		if not soup:
			return False
		
		result = []
		next_page_url = False
		
		next_page = soup.select_one('.page-item:last-child a.page-link')
		if next_page and ('Next' in next_page.decode_contents()):
			next_page_url = HistoryCrawler.endpoint_url_root.format(next_page['href'])
			print("Found next page url", next_page_url)
		else:
			print("Could not find next page url, this must be the last page.")
			
		news = soup.select('div.kars-list-alternate')
		for p in news:
			found = False
			for n in p.select('div.kars-news-header > .item'):
				primary_header = n.select_one('h1')
				secondary_header = n.select_one('h2')
				if not primary_header or not secondary_header:
					continue
					
				timestamps = n.select('h2 span.kars-data-ts')
				if len(timestamps) != 2:
					continue
					
				if 'Event' not in secondary_header.decode_contents().strip():
					continue
				
				item_title = primary_header.decode_contents().strip()
				# print(item_title)
				
				if 'Event' in item_title:
					event_info = re.findall(r"(.*) Event: (.*)", item_title)
					
					if not event_info or len(event_info[0]) != 2:
						print("Could not parse event info", item_title)
						continue
						
					event_type = event_info[0][0]
					event_title = event_info[0][1]
				else:
					event_type = None
					event_title = item_title
				
				# print(event_type, event_title)
				
				# if not event_type:
				# 	print("Could not retrieve event type")
				# 	continue
				
				# if not event_title:
				# 	print("Could not retrieve event title")
				# 	continue
				
				try:
					start_ts = int(float(timestamps[0]['data-ts']))
					start = datetime.utcfromtimestamp(start_ts)
					
					end_ts = int(float(timestamps[1]['data-ts']))
					end = datetime.utcfromtimestamp(end_ts)
				except:
					print("Could not parse event timestamps")
					continue
				
				found = True
			
			if not found: continue
			
			cards_link = p.select_one('div.kars-card-brief-list > a.btn-primary')
			if not cards_link:
				print("Could not find cards link!")
				continue
				
			card_ordinals = re.findall(r'(\d{1,})', cards_link['href'])
			if not card_ordinals:
				print("Could not find any card ordinals!", cards_link)
				continue
			
			card_ordinals = [int(x) for x in card_ordinals]
			
			result.append({
				'title' : event_title,
				'type'  : event_type,
				'start' : start,
				'end'   : end,
				'cards' : card_ordinals,
			})
			
		return result, next_page_url
		
	def _request_page(self, url):
		r = requests.get(url, headers={
			'User-Agent' : Config.USER_AGENT,
			# 'Referer'    : 'https://allstars.kirara.ca/en/history/',
		})
		
		if r.status_code != 200:
			print("Request failed", r.status_code)
			print(r.text)
			raise HistoryCrawlerException("Request failed")
		
		return r.content
		
	def _remove_duplicates(self, events):
		output = []
		seen = set()
		for d in events:
			t = hash(d['title'])
			if t not in seen:
				seen.add(t)
				output.append(d)
		return output
	
	def crawl_events(self, known_events = []):
		events_per_locale = defaultdict(list)
		for locale in ['en', 'jp']:
			events = []
			
			next_page_url = HistoryCrawler.endpoint_url_page.format(1).format(locale)
			while True:
				print("Crawling page url", next_page_url)
				
				html_data = self._request_page(next_page_url)
				
				event_data, next_page_url = self._parse_page(html_data)
				if event_data == False:
					raise HistoryCrawlerException("Failed to parse page data")
				
				events.extend(event_data)
				
				if any(x['title'] in known_events for x in event_data):
					print("Found a known event in the list, no need to continue crawling")
					break
				
				if next_page_url == False:
					break
				time.sleep(0.05)
			
			events = self._remove_duplicates(events)
			events = list(sorted(events, key=itemgetter('start')))
			events_per_locale[locale] = events
		
		output = []
		for event_en, event_jp in zip(events_per_locale["en"], events_per_locale["jp"]):
			if event_en['title'] in known_events or event_jp['title'] in known_events:
				continue
			
			if not all(x == y for x, y in zip(sorted(event_en['cards']), sorted(event_jp['cards']))):
				# print(event_en, event_jp)
				raise HistoryCrawlerException("Event cards do not match between the two locales!")
			
			event = {
				'type'     : event_en['type'],
				
				'title_en' : event_en['title'],
				'start_en' : event_en['start'].isoformat(),
				'end_en'   : event_en['end'].isoformat(),
				
				'title_jp' : event_jp['title'],
				'start_jp' : event_jp['start'].isoformat(),
				'end_jp'   : event_jp['end'].isoformat(),
				
				'cards'    : event_en['cards']
			}
			# print(event)
			output.append(event)
			
		return output

##################################

if __name__ == "__main__":
	hc = HistoryCrawler()
	known_events = []
	hc.crawl_events(known_events);
