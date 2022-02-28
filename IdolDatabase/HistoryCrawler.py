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
		
	# ------------------------------------------------------------------------------------
		
	def _try_find_next_page(self, soup):
		next_page = soup.select_one('.page-item:last-child a.page-link')
		if next_page and ('Next' in next_page.decode_contents()):
			next_page_url = HistoryCrawler.endpoint_url_root.format(next_page['href'])
			print("  Found next page url", next_page_url)
			return next_page_url
		else:
			print("  Could not find next page url, this must be the last page.")
			
		return False
		
	# ------------------------------------------------------------------------------------
	
	def _parse_banners(self, soup):
		banners_data = []
		banner_types = ['Spotlight', 'Festival', 'Party', 'Other']
		
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
					
				banner_type = None	
				
				secondary_header = secondary_header.decode_contents().strip()
				for needle in banner_types:
					if needle in secondary_header:
						banner_type = needle
				
				# Not a banner or of right type
				if banner_type == None:
					continue
				
				banner_title = primary_header.decode_contents().strip()
				
				try:
					start_ts = int(float(timestamps[0]['data-ts']))
					start = datetime.utcfromtimestamp(start_ts).replace(tzinfo=timezone.utc)
					
					end_ts = int(float(timestamps[1]['data-ts']))
					end = datetime.utcfromtimestamp(end_ts).replace(tzinfo=timezone.utc)
				except:
					print("  Could not parse banner timestamps")
					continue
				
				found = True
			
			if not found:
				continue
			
			cards_link = p.select_one('div.kars-card-brief-list > a.btn-primary')
			if not cards_link:
				print("  Could not find cards link!")
				continue
				
			card_ordinals = re.findall(r'(\d{1,})', cards_link['href'])
			if not card_ordinals:
				print("  Could not find any card ordinals!", cards_link)
				continue
			
			card_ordinals = [int(x) for x in card_ordinals]
			card_ordinals.sort()
			
			data = {
				'title' : banner_title,
				'type'  : banner_type,
				'start' : start,
				'end'   : end,
				'cards' : card_ordinals,
			}
			banners_data.append(data)
			
		return banners_data
		
	# ------------------------------------------------------------------------------------
	
	def _parse_events(self, soup):
		events_data = []
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
						print("  Could not parse event info", item_title)
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
					start = datetime.utcfromtimestamp(start_ts).replace(tzinfo=timezone.utc)
					
					end_ts = int(float(timestamps[1]['data-ts']))
					end = datetime.utcfromtimestamp(end_ts).replace(tzinfo=timezone.utc)
				except:
					print("  Could not parse event timestamps")
					continue
				
				found = True
			
			if not found:
				continue
			
			cards_link = p.select_one('div.kars-card-brief-list > a.btn-primary')
			if not cards_link:
				print("  Could not find cards link!")
				continue
				
			card_ordinals = re.findall(r'(\d{1,})', cards_link['href'])
			if not card_ordinals:
				print("  Could not find any card ordinals!", cards_link)
				continue
			
			card_ordinals = [int(x) for x in card_ordinals]
			card_ordinals.sort()
			
			data = {
				'title' : event_title,
				'type'  : event_type,
				'start' : start,
				'end'   : end,
				'cards' : card_ordinals,
			}
			events_data.append(data)
			
		return events_data
		
	# ------------------------------------------------------------------------------------
		
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
		
	# ------------------------------------------------------------------------------------
	
	def _cards_hash(self, ordinals_list):
		return hash(','.join([str(ordinal) for ordinal in ordinals_list]))
		
	def _remove_duplicates(self, events):
		output = []
		seen = set()
		for d in events:
			t = self._cards_hash(d['cards'])
			if t not in seen:
				seen.add(t)
				output.append(d)
		return output
		
	# ------------------------------------------------------------------------------------
	
	def crawl_history(self, known_events = [], known_banners_hashes = []):
		events_per_locale = defaultdict(list)
		banners = defaultdict(list)
		
		for locale in ['en', 'jp']:
			events = []
			
			crawling_events = True
			crawling_banners = (locale == 'jp')
			
			next_page_url = HistoryCrawler.endpoint_url_page.format(1).format(locale)
			while True:
				print("Crawling history page", next_page_url)
				
				html_data = self._request_page(next_page_url)
				
				html_soup = BeautifulSoup(html_data, 'html.parser')
				if not html_soup:
					raise HistoryCrawlerException("Failed to parse html code")
					
				next_page_url = self._try_find_next_page(html_soup)
				
				if crawling_banners:
					banner_data = self._parse_banners(html_soup)
					if banner_data == False:
						raise HistoryCrawlerException("Failed to parse page banners")
					
					banners.extend(banner_data)
					
					for banner in banner_data:
						cards_hash = self._cards_hash(banner['cards'])
						if cards_hash in known_banners_hashes:
							print("  Found a known banner in the list, no need to continue crawling banners!")
							crawling_banners = False
							break
				
				if crawling_events:
					event_data = self._parse_events(html_soup)
					if event_data == False:
						raise HistoryCrawlerException("Failed to parse page events")
					
					events.extend(event_data)
					
					if any(x['title'] in known_events for x in event_data):
						print("  Found a known event in the list, no need to continue crawling events!")
						crawling_events = False
					
				if not crawling_events and not crawling_banners:
					print("Not crawling events nor banners anymore. Breaking loop...")
					break
				
				if next_page_url == False:
					break
				time.sleep(0.5)
			
			events = self._remove_duplicates(events)
			events.sort(key=itemgetter('start'))
			events_per_locale[locale] = events
			
			banners = self._remove_duplicates(banners)
			banners.sort(key=itemgetter('start'))
		
		output = {
			'events'  : [],
			'banners' : [],
		}
		for event_en, event_jp in zip(events_per_locale["en"], events_per_locale["jp"]):
			if event_en['title'] in known_events or event_jp['title'] in known_events:
				continue
			
			if not all(x == y for x, y in zip(event_en['cards'], event_jp['cards'])):
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
			output['events'].append(event)
		
		for banner in banners:
			data = {
				'type'     : banner['type'],
				
				'title_jp' : banner['title'],
				'start_jp' : banner['start'].isoformat(),
				'end_jp'   : banner['end'].isoformat(),
				
				'cards'    : banner['cards']
			}
			output['banners'].append(data)
			
		return output
		
# ------------------------------------------------------------------------------------

if __name__ == "__main__":
	hc = HistoryCrawler()
	known_events = []
	hc.crawl_history(known_events);
