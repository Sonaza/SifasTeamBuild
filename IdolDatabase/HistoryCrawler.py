import Config

import re
import requests
import time
import json
import hashlib
from bs4 import BeautifulSoup
from operator import itemgetter
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from colorama import Fore
from colorama import Style

try:
	from .Enums import *
except:
	from Enums import *
	
	from colorama import init as colorama_init
	colorama_init(autoreset=True, strip=True)
	

class HistoryCrawlerException(Exception): pass
class HistoryCrawler:
	endpoint_url_root = "https://allstars.kirara.ca{:s}"
	endpoint_url_page = "https://allstars.kirara.ca/{{:s}}/history/{:d}"
			
	# ------------------------------------------------------------------------------------
	
	@staticmethod
	def hash_ordinals(ordinals_list):
		return hashlib.sha1(','.join([str(ordinal) for ordinal in ordinals_list]).encode('utf-8')).hexdigest()
	
	@staticmethod
	def remove_duplicates(items):
		output = []
		seen_items = set()
		for item in items:
			cards_hash = HistoryCrawler.hash_ordinals(item['cards'])
			if cards_hash not in seen_items:
				seen_items.add(cards_hash)
				output.append(item)
		return output

	# ------------------------------------------------------------------------------------
	
	banner_types = ['Spotlight', 'Festival', 'Party', 'Other']
	source_types = {
		'Spotlight' : Source.Spotlight,
		'Festival'  : Source.Festival,
		'Party'     : Source.Party,
		'Other'     : Source.Unspecified,
	}
	
	def parse_banners(self, soup, current_locale):
		banners_data = []
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
				for needle in self.banner_types:
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
					print(f"    {Fore.RED}{Style.BRIGHT}Could not parse banner timestamps for '{banner_title}'{Style.RESET_ALL}")
					continue
				
				found = True
			
			if not found: continue
			
			# Try to find list of card ordinals relevant to this banner
			cards_link = p.select_one('div.kars-card-brief-list > a.btn-primary')
			if not cards_link:
				print(f"    {Fore.RED}{Style.BRIGHT}Could not find cards link!{Style.RESET_ALL}")
				continue
				
			card_ordinals = re.findall(r'(\d{1,})', cards_link['href'])
			if not card_ordinals:
				print(f"    {Fore.RED}{Style.BRIGHT}Could not find any card ordinals!  {cards_link}{Style.RESET_ALL}")
				continue
			
			card_ordinals = [int(x) for x in card_ordinals]
			card_ordinals.sort()
			
			# Update fallback
			source_type = Source.Unspecified
			if banner_type in self.source_types:
				source_type = self.source_types[banner_type]
				
			for ordinal in card_ordinals:
				if ordinal not in self.fallback_data: self.fallback_data[ordinal] = {}
				
				if 'source' not in self.fallback_data[ordinal] or self.fallback_data[ordinal]['source'] == Source.Unspecified.value:
					self.fallback_data[ordinal]['source'] = source_type.value
				
				if current_locale == 'jp':
					self.fallback_data[ordinal]['release_date_jp'] = start.isoformat()
					
				if current_locale == 'en':
					self.fallback_data[ordinal]['release_date_ww'] = start.isoformat()
				
			# Finally append to list
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
	
	def parse_events(self, soup, current_locale):
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
				
				if 'Event:' in item_title:
					event_info = re.findall(r"(.*) Event: (.*)", item_title)
					
					if not event_info or len(event_info[0]) != 2:
						print(f"    {Fore.RED}{Style.BRIGHT}Could not parse event info:   {item_title}{Style.RESET_ALL}")
						continue
						
					event_type = event_info[0][0]
					event_title = event_info[0][1]
				else:
					event_type = None
					event_title = item_title
				
				try:
					start_ts = int(float(timestamps[0]['data-ts']))
					start = datetime.utcfromtimestamp(start_ts).replace(tzinfo=timezone.utc)
					
					end_ts = int(float(timestamps[1]['data-ts']))
					end = datetime.utcfromtimestamp(end_ts).replace(tzinfo=timezone.utc)
				except:
					print(f"    {Fore.RED}{Style.BRIGHT}Could not parse event timestamps!{Style.RESET_ALL}")
					continue
				
				found = True
				
			if not found:
				continue
				
			# Update fallback
			gacha_release_date = (start - timedelta(hours=72)).isoformat()
			event_release_date = start.isoformat()
			
			for g in p.select('div.grouped-card-icon-list > .group'):
				label = g.select_one('div.label')
				if not label:
					continue
				
				cards = []
				for card in g.select('a.card-icon'):
					ordinal = re.findall(r"(\d{1,})", card['href'])
					if ordinal:
						cards.append(int(ordinal[0]))
					else:
						raise HistoryCrawlerException("Could not parse card ordinal from link")
				
				label = label.decode_contents().strip()
				if label == 'Scouting' or label == 'Part 1' or label == 'Part 2':
					for ordinal in cards:
						if ordinal not in self.fallback_data:
							self.fallback_data[ordinal] = {}
						if 'source' not in self.fallback_data[ordinal]:
							self.fallback_data[ordinal]['source'] = Source.Gacha.value
						if current_locale == 'jp':
							self.fallback_data[ordinal]['release_date_jp'] = gacha_release_date
						if current_locale == 'en':
							self.fallback_data[ordinal]['release_date_ww'] = gacha_release_date
						
				elif label == 'Event':
					for ordinal in cards:
						if ordinal not in self.fallback_data:
							self.fallback_data[ordinal] = {}
						if 'source' not in self.fallback_data[ordinal]:
							self.fallback_data[ordinal]['source'] = Source.Event.value
						if current_locale == 'jp':
							self.fallback_data[ordinal]['release_date_jp'] = event_release_date
						if current_locale == 'en':
							self.fallback_data[ordinal]['release_date_ww'] = event_release_date
					
				else:
					print(label)
					raise HistoryCrawlerException("Unexpected card label")
			
			cards_link = p.select_one('div.kars-card-brief-list > a.btn-primary')
			if not cards_link:
				print(f"    {Fore.RED}{Style.BRIGHT}Could not find cards link!{Style.RESET_ALL}")
				continue
				
			card_ordinals = re.findall(r'(\d{1,})', cards_link['href'])
			if not card_ordinals:
				print(f"    {Fore.RED}{Style.BRIGHT}Could not find any card ordinals!  {cards_link}{Style.RESET_ALL}")
				continue
			
			card_ordinals = [int(x) for x in card_ordinals]
			card_ordinals.sort()
			
			data = {
				'title'       : event_title,
				'type'        : event_type,
				'start'       : start,
				'end'         : end,
				'cards'       : card_ordinals,
			}
			events_data.append(data)
		
		return events_data
		
	# ------------------------------------------------------------------------------------
		
	def request_page_html(self, url):
		r = requests.get(url, headers={
			'User-Agent' : Config.USER_AGENT,
			# 'Referer'    : 'https://allstars.kirara.ca/en/history/',
		})
		
		if r.status_code != 200:
			print(f"  {Fore.RED}{Style.BRIGHT}Request failed  {r.status_code}{Style.RESET_ALL}")
			print(r.text)
			raise HistoryCrawlerException("Request failed")
		
		return r.content
		
	# ------------------------------------------------------------------------------------
	
	def load_data_fallback(self):
		try:
			with open(Config.DATA_FALLBACK_FILE, "r", encoding="utf-8") as f:
				self.fallback_data = json.load(fp=f)
				f.close()
			return True
		except Exception as e:
			self.fallback_data = {}
		return False
		
	
	def save_data_fallback(self):
		try:
			with open(Config.DATA_FALLBACK_FILE, "w", encoding="utf-8") as f:
				json.dump(self.fallback_data, fp=f)
			return True
			
		except Exception as e:
			print("Failed to save fallback file. ", e)
			
		return False
		
	# ------------------------------------------------------------------------------------
	
	def crawl_history(self, known_events = [], known_banners_hashes = []):
		self.load_data_fallback()
		
		events_per_locale = defaultdict(list)
		banners_per_locale = defaultdict(list)
		
		for locale in ['en', 'jp']:
			events = []
			banners = []
			
			crawling_events = True 
			crawling_banners = True
			
			next_page_url = self.endpoint_url_page.format(1).format(locale)
			while True:
				print(f"  {Fore.YELLOW}Crawling {locale.upper()} locale history  {Fore.WHITE}{Style.BRIGHT}: {next_page_url}{Style.RESET_ALL}")
				
				html_data = self.request_page_html(next_page_url)
				html_soup = BeautifulSoup(html_data, 'html.parser')
				if not html_soup:
					raise HistoryCrawlerException("Failed to parse html code")
				
				next_page = html_soup.select_one('.page-item:last-child a.page-link')
				if next_page and ('Next' in next_page.decode_contents()):
					next_page_url = self.endpoint_url_root.format(next_page['href'])
				else:
					next_page_url = False
					print(f"    {Fore.YELLOW}{Style.BRIGHT}Could not find next page url, this must be the last page.{Style.RESET_ALL}")
				
				if crawling_banners:
					banner_data = self.parse_banners(html_soup, locale)
					if banner_data == False:
						raise HistoryCrawlerException("Failed to parse page banners")
					
					banners.extend(banner_data)
					for banner in banner_data:
						cards_hash = self.hash_ordinals(banner['cards'])
						if cards_hash in known_banners_hashes:
							print(f"    {Fore.WHITE}{Style.BRIGHT}Found a known banner in the list. {Fore.GREEN}Done!{Style.RESET_ALL}")
							crawling_banners = False
							break
							
							
				if crawling_events:
					event_data = self.parse_events(html_soup, locale)
					if event_data == False:
						raise HistoryCrawlerException("Failed to parse page events")
					
					events.extend(event_data)
					if any(x['title'] in known_events for x in event_data):
						print(f"    {Fore.WHITE}{Style.BRIGHT}Found a known event in the list. {Fore.GREEN}Done!{Style.RESET_ALL}")
						crawling_events = False
						
					
				if not crawling_events and not crawling_banners:
					print(f"  {Fore.GREEN}{Style.BRIGHT}{locale.upper()} history crawl complete!{Style.RESET_ALL}")
					break
				
				if next_page_url == False:
					break
				time.sleep(0.5)
			
			events = self.remove_duplicates(events)
			events.sort(key=itemgetter('start'))
			events_per_locale[locale] = events
			
			banners = self.remove_duplicates(banners)
			banners.sort(key=itemgetter('start'))
			banners_per_locale[locale] = banners
		
		output = {
			'events'  : [],
			'banners' : [],
		}
		
		events_data_by_card_hash = defaultdict(dict)
		for locale, events in events_per_locale.items():
			for event in events:
				if event['title'] in known_events:
					# print(event['title'], "found in known events. Skipping...")
					continue
				
				cards_hash = self.hash_ordinals(event['cards'])
				events_data_by_card_hash[cards_hash][locale] = event
		
		for cards_hash, event_data_by_locale in events_data_by_card_hash.items():
			if not ('en' in event_data_by_locale and 'jp' in event_data_by_locale):
				print(event_data_by_locale)
				raise HistoryCrawlerException("Missing event data for one locale!")
			
			event_en, event_jp = event_data_by_locale['en'], event_data_by_locale['jp']
			
			event = {
				'type'       : event_en['type'],
				
				'title_jp'   : event_jp['title'],
				'start_jp'   : event_jp['start'].isoformat(),
				'end_jp'     : event_jp['end'].isoformat(),
				
				'title_ww'   : event_en['title'],
				'start_ww'   : event_en['start'].isoformat(),
				'end_ww'     : event_en['end'].isoformat(),
				
				'cards'      : event_jp['cards'],
				'cards_hash' : cards_hash,
			}
			output['events'].append(event)
		
		# -----------------------------------------
		
		banners_data_by_card_hash = defaultdict(dict)
		for locale, banners in banners_per_locale.items():
			for banner in banners:
				cards_hash = self.hash_ordinals(banner['cards'])
				if cards_hash in known_banners_hashes:
					continue
				banners_data_by_card_hash[cards_hash][locale] = banner
				
		for cards_hash, banner_data_by_locale in banners_data_by_card_hash.items():
			if not ('en' in banner_data_by_locale and 'jp' in banner_data_by_locale):
				# print("Missing banner data for one locale!", banner_data_by_locale)
				# raise HistoryCrawlerException("Missing banner data for one locale!")
				continue
			
			banner_en, banner_jp = banner_data_by_locale['en'], banner_data_by_locale['jp']
			
			data = {
				'type'       : banner_jp['type'],
				
				'title_jp'   : banner_jp['title'],
				'start_jp'   : banner_jp['start'].isoformat(),
				'end_jp'     : banner_jp['end'].isoformat(),
				
				'title_ww'   : banner_en['title'],
				'start_ww'   : banner_en['start'].isoformat(),
				'end_ww'     : banner_en['end'].isoformat(),
				
				'cards'      : banner_jp['cards'],
				'cards_hash' : cards_hash,
			}
			output['banners'].append(data)
		
		self.save_data_fallback()
		
		return output
		
# ------------------------------------------------------------------------------------

if __name__ == "__main__":
	hc = HistoryCrawler()
	known_events = []
	result = hc.crawl_history(known_events)
	print(result)
