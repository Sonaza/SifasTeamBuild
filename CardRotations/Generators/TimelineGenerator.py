import Config
from IdolDatabase import *

from CardRotations import GeneratorBase
from ..Utility import Utility

import json
from operator import itemgetter
from datetime import datetime, timezone
from calendar import monthrange
		
class TimelineGenerator(GeneratorBase):
	def __init__(self, parent):
		super().__init__(parent)
	
	# force_render  = True
	used_templates = ["timeline.html", "timeline_month.html"]
	
	timeline_day_width       = 20
	timeline_thumbnail_width = 36
		
	def generate_and_render(self):
		timeline_for_locale, monthly_equivalence = self.get_card_timeline()
		for locale in Locale:
			timeline, entry_info, metadata_json = timeline_for_locale[locale]
			for release_month, timeline_month in timeline['entries'].items():
				self.render_and_save("timeline_month.html", f"pages/deferred/timeline{locale.suffix}_{release_month}.html", {
						'release_month'       : release_month,
						'timeline_month'      : timeline_month,
						'timeline'            : timeline,
						'entry_info'          : entry_info,
						'timeline_day_width'       : self.timeline_day_width,
						'timeline_thumbnail_width' : self.timeline_thumbnail_width,
					}, minify=not self.args.dev)
				
			self.render_and_save("timeline.html", f"pages/timeline{locale.suffix}.html", {
					'metadata_json'       : metadata_json,
					'locale'              : locale,
					'timeline'            : timeline,
					'entry_info'          : entry_info,
					'monthly_equivalence' : monthly_equivalence if locale == Locale.JP else Utility.swap_keys_and_values(monthly_equivalence),
				}, minify=not self.args.dev)
		
		return True
		
	
	def get_card_timeline(self):
		now = datetime.now(timezone.utc)
		current_month  = now.strftime("%Y-%m")
		
		game_release_months = {
			Locale.JP : "2019-09",
			Locale.WW : "2020-02",
		}
		
		date_format = "%B %Y"
		
		timeline_for_locale = {}
		monthly_equivalence = {}
		
		from collections import Counter
		
		idols_data = self.client.get_idols(rarity=[Rarity.UR, Rarity.SR], with_event_info=True, with_banner_info=True)
		for idol in idols_data:
			release_month = idol.release_date[Locale.JP].strftime("%Y-%m")
			if release_month not in monthly_equivalence: monthly_equivalence[release_month] = []
			monthly_equivalence[release_month].append(idol.release_date[Locale.WW].strftime("%Y-%m"))
			
		for release_month, global_months in monthly_equivalence.items():
			counted = list(Counter(global_months).items())
			counted.sort(key=lambda x:-x[1])
			equivalent_global_month = counted[0][0]
			monthly_equivalence[release_month] = equivalent_global_month
		
		for locale in Locale:
			timeline = {
				'events'  : {},
				'banners' : {},
				'entries' : {},
			}
			entry_info = {}
			for idol in idols_data:
				release_date  = idol.release_date[locale]
				release_month = release_date.strftime("%Y-%m")
				
				month_start = release_date.replace(day=1, hour=0, minute=0, second=0)
				
				if release_month not in timeline['entries']:
					timeline['entries'][release_month] = {group: {member.member_id: {} for member in Idols.by_group[group]} for group in Group}
					
					days_in_month      = monthrange(release_date.year, release_date.month)[1]
					month_length_days  = days_in_month
					month_start_offset = 0
					
					if release_month == game_release_months[locale]:
						month_length_days  = 9
						month_start_offset = days_in_month - month_length_days
						
					elif release_month == current_month:
						month_length_days  = min(days_in_month, math.ceil((now.day) / 12) * 15)
						
					if release_month not in entry_info: entry_info[release_month] = {}
					entry_info[release_month]['start']   = month_start + timedelta(days=month_start_offset)
					entry_info[release_month]['end']     = month_start + timedelta(days=month_start_offset) + timedelta(days=month_length_days)
					entry_info[release_month]['days']    = month_length_days
					
					if 'events' not in entry_info[release_month]:
						entry_info[release_month]['events']  = set()
					if 'banners' not in entry_info[release_month]:
						entry_info[release_month]['banners'] = set()
						
				current_bucket = timeline['entries'][release_month][idol.group_id][idol.member_id]
				
				days_from_start = (release_date - entry_info[release_month]['start']).days
				if days_from_start not in current_bucket:
					current_bucket[days_from_start] = []
					
				current_bucket[days_from_start].append(idol)
				if len(current_bucket[days_from_start]) > 1:
					current_bucket[days_from_start].sort(key=lambda x: -x.rarity.value)
				
				# --------------------------------------------------------------
					
				if idol.event.id:
					if idol.source == Source.Event and idol.event.id not in timeline['events']:
						idol.event.start[locale] = idol.event.start[locale].replace(hour=0, minute=0, second=0)
						idol.event.end[locale]   = idol.event.end[locale].replace(hour=0, minute=0, second=0)
						timeline['events'][idol.event.id] = {
							'info'            : idol.event,
							'duration'        : (idol.event.end[locale] - idol.event.start[locale]).days + 1,
							'days_from_start' : (idol.event.start[locale] - entry_info[release_month]['start']).days,
							'timespan' : {
								'start': (idol.event.start[locale], (idol.event.start[locale].year, idol.event.start[locale].month, idol.event.start[locale].day)),
								'end'  : (idol.event.end[locale],   (idol.event.end[locale].year, idol.event.end[locale].month, idol.event.end[locale].day)),
							},
						}
						
						start_key = idol.event.start[locale].strftime("%Y-%m")
						entry_info[start_key]['events'].add(idol.event.id)
						
						end_key = idol.event.end[locale].strftime("%Y-%m")
						if end_key not in entry_info:           entry_info[end_key] = {}
						if 'events' not in entry_info[end_key]: entry_info[end_key]['events']  = set()
						entry_info[end_key]['events'].add(idol.event.id)
				
				# --------------------------------------------------------------
				
				allowed_sources = [Source.Spotlight, Source.Gacha, Source.Festival, Source.Party]
				if idol.banner.id and idol.source in allowed_sources and idol.banner.id not in timeline['banners']:
					idol.banner.start[locale] = idol.banner.start[locale].replace(hour=0, minute=0, second=0)
					idol.banner.end[locale]   = idol.banner.end[locale].replace(hour=0, minute=0, second=0)
					timeline['banners'][idol.banner.id] = {
						'info'            : idol.banner,
						'duration'        : (idol.banner.end[locale] - idol.banner.start[locale]).days + 1,
						'days_from_start' : (idol.banner.start[locale] - entry_info[release_month]['start']).days,
						'timespan' : {
							'start': (idol.banner.start[locale], (idol.banner.start[locale].year, idol.banner.start[locale].month, idol.banner.start[locale].day)),
							'end'  : (idol.banner.end[locale],   (idol.banner.end[locale].year, idol.banner.end[locale].month, idol.banner.end[locale].day)),
						},
					}
					
					start_key = idol.banner.start[locale].strftime("%Y-%m")
					entry_info[start_key]['banners'].add(idol.banner.id)
					
					end_key = idol.banner.end[locale].strftime("%Y-%m")
					if end_key not in entry_info:            entry_info[end_key] = {}
					if 'banners' not in entry_info[end_key]: entry_info[end_key]['banners'] = set()
					entry_info[end_key]['banners'].add(idol.banner.id)
				
			# --------------------------------------------------------------
			
			metadata_json = {
				'events'  : {},
				'banners' : {},
				'months'  : {},
			}
			
			events, _ = self.event_history_generator.get_events_with_cards()
			for event_id, event_data in timeline['events'].items():
				featured_member = events[event_id]['free'][0].member_id
				event_gacha_urs = [card.member_id for card in events[event_id]['gacha'] if card.rarity == Rarity.UR]
				metadata_json['events'][event_id] = {
					'title'        : event_data['info'].title,
					'featured'     : featured_member,
					'gacha'        : event_gacha_urs,
					# 'members'      : Utility.concat([card.member_id.name for card in events[event_id]['free']], separator=', '),
					'type'         : event_data['info'].type,
					'start_offset' : event_data['days_from_start'],
					'duration'     : event_data['duration'],
					'timespan'     : event_data['timespan'],
				}
				
			banners = self.banners_generator.get_banners_with_cards()
			for banner_id, banner_data in timeline['banners'].items():
				metadata_json['banners'][banner_id] = {
					'title'        : banners[banner_id]['banner']['title'],
					'type'         : banner_data['info'].type,
					'start_offset' : banner_data['days_from_start'],
					'duration'     : banner_data['duration'],
					'timespan'     : banner_data['timespan'],
				}
			
			for release_month, entry_data in entry_info.items():
				start = entry_info[release_month]['start']
				if start.year not in metadata_json['months']:
					metadata_json['months'][start.year] = [entry_info[release_month]['start'].month, entry_info[release_month]['start'].month]
				metadata_json['months'][start.year][-1] = entry_info[release_month]['start'].month
				
			def json_serialize(obj):
			    if isinstance(obj, (Member, EventType, BannerType)):
			        return obj.value
			    if isinstance(obj, (datetime)):
			        return Utility.format_datestring(obj, long_month=True)
			    raise TypeError(f"Type {type(obj)} not serializable")
					
			metadata_json = json.dumps(metadata_json, separators=(',', ':'), default=json_serialize)
			
			timeline_for_locale[locale] = (timeline, entry_info, metadata_json)
		return timeline_for_locale, monthly_equivalence
	
