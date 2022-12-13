import re
import requests
import time
import json
from bs4 import BeautifulSoup
from operator import itemgetter
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from colorama import Fore
from colorama import Style

from .Config import Config
from .Enums import *

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
			# print(f"    {Fore.GREEN}{Style.BRIGHT}Found next page url  {Fore.WHITE}: {next_page_url}{Style.RESET_ALL}")
			return next_page_url
		else:
			print(f"    {Fore.YELLOW}{Style.BRIGHT}Could not find next page url, this must be the last page.{Style.RESET_ALL}")
			
		return False
		
	# ------------------------------------------------------------------------------------
	
	def _parse_banners(self, soup, update_fallback):
		banners_data = []
		
		banner_types = ['Spotlight', 'Festival', 'Party', 'Other']
		source_types = {
			'Spotlight' : Source.Spotlight,
			'Festival'  : Source.Festival,
			'Party'     : Source.Party,
			'Other'     : Source.Unspecified,
		}
		
		new_cards = {}
		
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
					print(f"    {Fore.RED}{Style.BRIGHT}Could not parse banner timestamps{Style.RESET_ALL}")
					continue
				
				found = True
			
			if not found:
				continue
			
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
			
			if update_fallback:
				source_type = Source.Unspecified
				if banner_type in source_types:
					source_type = source_types[banner_type]
					
				for ordinal in card_ordinals:
					new_cards[ordinal] = {
						'source'       : source_type.value,
						'release_date' : start.isoformat(),
					}
			
			data = {
				'title' : banner_title,
				'type'  : banner_type,
				'start' : start,
				'end'   : end,
				'cards' : card_ordinals,
			}
			
			banners_data.append(data)
		
		if update_fallback:
			self._append_cards_data_fallback(new_cards)
			
		return banners_data
		
	# ------------------------------------------------------------------------------------
	
	def _parse_events(self, soup, update_fallback):
		events_data = []
		
		new_cards = {}
		
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
					print(f"    {Fore.RED}{Style.BRIGHT}Could not parse event timestamps!{Style.RESET_ALL}")
					continue
				
				found = True
				
			if not found:
				continue
			
			if update_fallback:
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
							new_cards[ordinal] = {
								'source'       : Source.Gacha.value,
								'release_date' : gacha_release_date,
							}
						
					elif label == 'Event':
						for ordinal in cards:
							new_cards[ordinal] = {
								'source'       : Source.Event.value,
								'release_date' : event_release_date,
							}
						
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
		
		if update_fallback:
			self._append_cards_data_fallback(new_cards)
		
		return events_data
		
	# ------------------------------------------------------------------------------------
		
	def _request_page(self, url):
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
	
	def _append_cards_data_fallback(self, new_data):
		try:
			with open(Config.CARD_DATA_FALLBACK, "r", encoding="utf-8") as f:
				cards_data = json.load(fp=f)
				f.close()
		except Exception as e:
			print("  Couldn't load original data", e)
			cards_data = {}
		
		cards_data.update(new_data)
		
		try:
			with open(Config.CARD_DATA_FALLBACK, "w", encoding="utf-8") as f:
				json.dump(cards_data, fp=f)
		except Exception as e:
			print("Failed to append to sources fallback file. ", e)
			
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
				print(f"  {Fore.YELLOW}Crawling {locale.upper()} locale history  {Fore.WHITE}{Style.BRIGHT}: {next_page_url}{Style.RESET_ALL}")
				
				html_data = self._request_page(next_page_url)
				
				html_soup = BeautifulSoup(html_data, 'html.parser')
				if not html_soup:
					raise HistoryCrawlerException("Failed to parse html code")
					
				next_page_url = self._try_find_next_page(html_soup)
				
				if crawling_banners:
					banner_data = self._parse_banners(html_soup, locale == 'jp')
					if banner_data == False:
						raise HistoryCrawlerException("Failed to parse page banners")
					
					banners.extend(banner_data)
					
					for banner in banner_data:
						cards_hash = self._cards_hash(banner['cards'])
						if cards_hash in known_banners_hashes:
							print(f"    {Fore.WHITE}{Style.BRIGHT}Found a known banner in the list. {Fore.GREEN}Done!{Style.RESET_ALL}")
							crawling_banners = False
							break
				
				if crawling_events:
					event_data = self._parse_events(html_soup, locale == 'jp')
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
			
			events = self._remove_duplicates(events)
			events.sort(key=itemgetter('start'))
			events_per_locale[locale] = events
			
			banners = self._remove_duplicates(banners)
			banners.sort(key=itemgetter('start'))
		
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
				
				cardhash = self._cards_hash(event['cards'])
				events_data_by_card_hash[cardhash][locale] = event
		
		for _, event_data_by_locale in events_data_by_card_hash.items():
			if not ('en' in event_data_by_locale and 'jp' in event_data_by_locale):
				print(event_data_by_locale)
				raise HistoryCrawlerException("Missing event data for one locale!")
			
			event_en, event_jp = event_data_by_locale['en'], event_data_by_locale['jp']
			
			# print(event_en['title'], event_jp['title'])
			
			# if not all(x == y for x, y in zip(event_en['cards'], event_jp['cards'])):
			# 	print(event_en, event_jp)
			# 	raise HistoryCrawlerException("Event cards do not match between the two locales!")
			
			# if event_en['title'] in known_events or event_jp['title'] in known_events:
			# 	print(event_en['title'], event_jp['title'], "was found in known events")
			# 	continue
			
			event = {
				'type'     : event_en['type'],
				
				'title_en' : event_en['title'],
				'start_en' : event_en['start'].isoformat(),
				'end_en'   : event_en['end'].isoformat(),
				
				'title_jp' : event_jp['title'],
				'start_jp' : event_jp['start'].isoformat(),
				'end_jp'   : event_jp['end'].isoformat(),
				
				'cards'    : event_jp['cards']
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
