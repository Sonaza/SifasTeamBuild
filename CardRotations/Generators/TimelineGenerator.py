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
					}, minify_html=not self.args.dev)
				
			self.render_and_save("timeline.html", f"pages/timeline{locale.suffix}.html", {
					'metadata_json'       : metadata_json,
					'locale'              : locale,
					'timeline'            : timeline,
					'entry_info'          : entry_info,
					'monthly_equivalence' : monthly_equivalence if locale == Locale.JP else Utility.swap_keys_and_values(monthly_equivalence),
				}, minify_html=not self.args.dev)
		
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
		
		idols_data = self.client.get_idols(
			rarity = [Rarity.UR, Rarity.SR],
			with_event_info  = True,
			with_banner_info = True)
		
		for idol in idols_data:
			release_month = idol.release_date[Locale.JP].strftime("%Y-%m")
			if release_month not in monthly_equivalence: monthly_equivalence[release_month] = []
			monthly_equivalence[release_month].append(idol.release_date[Locale.WW].strftime("%Y-%m"))
			
		from collections import Counter
		
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
			for idol in sorted(idols_data, key=lambda idol: idol.release_date[locale]):
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
					if idol.event.id not in timeline['events']:
						timeline['events'][idol.event.id] = {
							'event'    : None,
							'banner'   : None,
							'summary'  : None,
						}
					
					event_bucket = timeline['events'][idol.event.id]
					
					if idol.source == Source.Event and not event_bucket['event']:
						idol.event.start[locale] = idol.event.start[locale].replace(hour=0, minute=0, second=0)
						idol.event.end[locale]   = idol.event.end[locale].replace(hour=0, minute=0, second=0)
						event_bucket['event'] = {
							'info'            : idol.event,
							'duration'        : (idol.event.end[locale] - idol.event.start[locale]).days + 1,
							'days_from_start' : (idol.event.start[locale] - entry_info[release_month]['start']).days,
							'timespan' : {
								'start': (idol.event.start[locale], (idol.event.start[locale].year, idol.event.start[locale].month, idol.event.start[locale].day)),
								'end'  : (idol.event.end[locale],   (idol.event.end[locale].year, idol.event.end[locale].month, idol.event.end[locale].day)),
							},
						}
					
					recheck_things = False
					if idol.source == Source.Gacha and not event_bucket['banner']:
						idol.event.start[locale] = idol.event.start[locale].replace(hour=0, minute=0, second=0)
						# idol.event.end[locale]   = idol.event.end[locale].replace(hour=0, minute=0, second=0)
						idol.release_date[locale]   = idol.release_date[locale].replace(hour=0, minute=0, second=0)
						
						if not event_bucket['banner'] or idol.release_date[locale] < event_bucket['banner']['timeline']['start'][0]:
							recheck_things = True
							event_bucket['banner'] = {
								'info'            : idol.event,
								'duration'        : (idol.event.start[locale] - idol.release_date[locale]).days + 1,
								'days_from_start' : (idol.release_date[locale] - entry_info[release_month]['start']).days,
								'timespan' : {
									'start': (idol.release_date[locale], (idol.release_date[locale].year, idol.release_date[locale].month, idol.release_date[locale].day)),
									'end'  : (idol.event.start[locale],  (idol.event.start[locale].year, idol.event.start[locale].month, idol.event.start[locale].day)),
								},
							}
					
					if (not event_bucket['summary'] or recheck_things) and event_bucket['event'] and event_bucket['banner']:
						full_start   = event_bucket['banner']['timespan']['start'][0]
						full_end     = event_bucket['event']['timespan']['end'][0]
						event_bucket['summary'] = {
							'info'            : idol.event,
							'duration'        : (full_end - full_start).days + 1,
							'days_from_start' : (full_start - entry_info[release_month]['start']).days,
							'timespan' : {
								'start': (full_start, (full_start.year, full_start.month, full_start.day)),
								'end'  : (full_end,   (full_end.year, full_end.month, full_end.day)),
							},
						}
						
						start_key = full_start.strftime("%Y-%m")
						entry_info[start_key]['events'].add(idol.event.id)
						
						end_key = full_end.strftime("%Y-%m")
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
					'title'        : event_data['summary']['info'].title,
					'featured'     : featured_member,
					'gacha'        : event_gacha_urs,
					'type'         : event_data['summary']['info'].type,
					'start_offset' : event_data['summary']['days_from_start'],
					'duration'     : event_data['summary']['duration'],
					'timespan'     : {
						**event_data['summary']['timespan'],
						'event'    : event_data['event']['timespan'],
						'banner'   : event_data['banner']['timespan'],
					}
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
			        return Utility.format_datestring(obj, long_month=True, with_year=False)
			    raise TypeError(f"Type {type(obj)} not serializable")
					
			metadata_json = json.dumps(metadata_json, separators=(',', ':'), default=json_serialize)
			
			timeline_for_locale[locale] = (timeline, entry_info, metadata_json)
		return timeline_for_locale, monthly_equivalence
	
