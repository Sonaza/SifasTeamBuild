import Config
from IdolDatabase import *

from CardRotations import GeneratorBase, CardValidity
from Common import Utility

from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta


from dataclasses import dataclass

@dataclass
class IdolElapsed:
	member    : Member
	idol      : KiraraIdol
	elapsed   : Optional[Dict[Locale, timedelta]]
	highlight : bool
	
	def __iter__(self):
		return iter((self.member, self.idol, self.elapsed, self.highlight))


class CardStatsGenerator(GeneratorBase):
	def __init__(self, parent):
		super().__init__(parent)
	
	used_templates = ["stats.html", "overdueness.html"]
		
	history_category = {
		Source.Unspecified : 'gacha',
		Source.Event       : 'event',
		Source.Gacha       : 'gacha',
		Source.Spotlight   : 'gacha',
		Source.Festival    : 'festival',
		Source.Party       : 'party',
	}

	def generate_and_render(self):
		general_stats, maximums = self.client.get_general_stats()
		self.render_and_save("stats.html", "pages/stats.html", {
			'category_tag'   : 'general',
			'general_stats'  : general_stats,
		}, minify_html=not self.args.dev)
		
		card_stats, category_info, category_has_empty_rows = self.get_card_stats()
		for category_tag in card_stats.keys():
			self.render_and_save("stats.html", f"pages/stats_{category_tag}.html", {
				'category_tag'     : category_tag,
				'category_data'    : card_stats[category_tag],
				'category_info'    : category_info[category_tag],
				'has_empty_rows'   : category_has_empty_rows[category_tag],
				'history_category' : self.history_category,
			}, minify_html=not self.args.dev)
	
	
		weighted_overdueness = self.client.get_weighted_overdueness()
		self.render_and_save("overdueness.html", f"pages/stats_overdueness.html", {
			'weighted_overdueness' : weighted_overdueness,
			'history_category'     : self.history_category,
		}, minify_html=not self.args.dev)
	
		return True
		
	#-----------------------------------------------------------------------------------------

	def process_time_elapsed(self, idols, group=None):
		now = datetime.now(timezone.utc)
		
		# Note down all idols
		all_idols = set()
		if group == None:
			for idol in Idols.all_idols:
				all_idols.add(idol.member_id)
		else:
			for idol in Idols.by_group[group]:
				all_idols.add(idol.member_id)
		
		# Calculate time since stats
		highlighted_idols = set()
		elapsed_list = []
		for idol in idols:
			duplicate = not (idol.member_id in all_idols)
			
			# member, card, time_since, highlight
			elapsed_list.append(IdolElapsed(idol.member_id, idol, {locale: now - idol.release_date[locale] for locale in Locale}, duplicate))
			
			if duplicate and idol.member_id not in highlighted_idols:
				highlighted_idols.add(idol.member_id)
				
			try:
				all_idols.remove(idol.member_id)
			except: pass
		
		# Highlight all duplicate idol entries
		for index, data in enumerate(elapsed_list):
			if data.member in highlighted_idols:
				data.highlight = True
		
		has_empty_rows = (len(all_idols) > 0)
		
		# Add dummy entries for idols not found in the dataset
		for member_id in all_idols:
			elapsed_list.insert(0, IdolElapsed(member_id, CardValidity.CardNonExtant(), None, False))
			
		return elapsed_list, has_empty_rows
		
		
	def get_newest_idols(self, group : Group = None, rarity : Rarity = None, source : Source = None):
		idols = self.client.get_newest_idols(group=group, rarity=rarity, source=source)
		
		now = datetime.now(tz=timezone.utc) - timedelta(hours=24)
		
		pending_members = []
		for idol in idols:
			if idol.release_date[Locale.JP] > now:
				pending_members.append(idol.member_id)
				
		if pending_members:
			previous_idols = self.client.get_newest_idols(group=group, rarity=rarity, source=source,
				members=pending_members, released_before=now)
			idols.extend(previous_idols)
			idols.sort(key=lambda x: x.release_date[Locale.JP])
			
		return idols
	
		
	def get_card_stats(self):
		categories = {
			'event'      : (Rarity.UR, [Source.Event], ),
			'festival'   : (Rarity.UR, [Source.Festival], ),
			'party'      : (Rarity.UR, [Source.Party], ),
			'limited'    : (Rarity.UR, [Source.Festival, Source.Party], ),
			'spotlight'  : (Rarity.UR, [Source.Spotlight, Source.Party], ),
			'nonlimited' : (Rarity.UR, [Source.Unspecified, Source.Gacha, Source.Spotlight,], ),
			'gacha'      : (Rarity.UR, [Source.Unspecified, Source.Gacha, Source.Spotlight, Source.Festival, Source.Party], ),
			'ur'         : (Rarity.UR, None, ),
			'sr'         : (Rarity.SR, None, ),
			'all'        : ([Rarity.UR, Rarity.SR], None, ),
		}
		category_info = {
			'event'      : ( "Event UR",             "Event URs awarded in item exchange and story events." ),
			'festival'   : ( "Festival UR",          "Festival limited URs scouted exclusively from All Stars Festival banners." ),
			'party'      : ( "Party UR",             "Party limited URs scouted exclusively from Party Scouting banners." ),
			'limited'    : ( "Limited UR",           "The most recent Festival and Party limited URs. Due to their higher average power level and limited nature, the same girl should be unlikely to receive two in quick succession." ),
			'spotlight'  : ( "Party + Spotlight UR", "Party banners replaced Spotlight banners upon their introduction." ),
			'nonlimited' : ( "Non-Limited Gacha UR", "Any non-limited UR scouted from banners using Star Gems." ),
			'gacha'      : ( "Any Gacha UR",         "Any UR scouted from banners using Star Gems." ),
			'ur'         : ( "Any UR",               "Any most recent UR, free or otherwise." ),
			'sr'         : ( "Any SR",               "Any most recent SR, free or otherwise." ),
			'all'        : ( "All",                  "Any most recent UR or SR, free or otherwise." ),
		}
		
		limited_sources = {
			'festival'  : [Source.Festival],
			'party'     : [Source.Party],
			'limited'   : [Source.Festival, Source.Party],
			'spotlight' : [Source.Party],
		}
		limited_idols, max_per_source = self.client.get_idols_by_source_and_member([Source.Festival, Source.Party])
		
		category_data = defaultdict(dict)
		category_has_empty_rows = defaultdict(bool)
		
		now = datetime.now(tz=timezone.utc)
		
		for category, (rarity, sources) in categories.items():
			for group in Group:
				elapsed_list, has_empty_rows = self.process_time_elapsed(idols=self.get_newest_idols(group=group, rarity=rarity, source=sources), group=group)
				category_data[category][group.tag] = {
					'display_name'    : group.display_name,
					'cards'           : elapsed_list,
					'has_empty_rows'  : has_empty_rows,
					'show_source'     : (not isinstance(sources, list) or len(sources) > 1),
					'show_rarity'     : (isinstance(rarity, list) and len(rarity) > 1),
					'limited_idols'   : limited_idols,
					'limited_sources' : (limited_sources[category] if category in limited_sources else []),
					'max_per_source'  : max_per_source,
				}
				category_has_empty_rows[category] = has_empty_rows or category_has_empty_rows[category]
				
			elapsed_list, has_empty_rows = self.process_time_elapsed(idols=self.get_newest_idols(rarity=rarity, source=sources), group=None)
			category_data[category]['collapsed'] = {
				'display_name'    : '',
				'cards'           : elapsed_list,
				'has_empty_rows'  : has_empty_rows,
				'show_source'     : (not isinstance(sources, list) or len(sources) > 1),
				'show_rarity'     : (isinstance(rarity, list) and len(rarity) > 1),
				'limited_idols'   : limited_idols,
				'limited_sources' : (limited_sources[category] if category in limited_sources else []),
				'max_per_source'  : max_per_source,
			}
			category_has_empty_rows[category] = has_empty_rows or category_has_empty_rows[category]
		
		return category_data, category_info, category_has_empty_rows
	
