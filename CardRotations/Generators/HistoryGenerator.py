import Config
from IdolDatabase import *

from CardRotations import GeneratorBase
from Common import Utility

from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

from dataclasses import dataclass


class HistoryGenerator(GeneratorBase):
	def __init__(self, parent):
		super().__init__(parent)
		
	used_templates = ["history_frontpage.html", "history_stats.html"]
	
	history_category = {
		Source.Unspecified : 'gacha',
		Source.Event       : 'event',
		Source.Gacha       : 'gacha',
		Source.Spotlight   : 'gacha',
		Source.Festival    : 'festival',
		Source.Party       : 'party',
	}
	
	# def due_for_rendering(self):
	# 	return any([self.due_for_rendering(), self.due_for_rendering()])

	def generate_and_render(self):
		self.render_and_save("history_frontpage.html", "pages/history.html", {}, minify_html=not self.args.dev)
		
		member_addition_dates = self.client.get_member_addition_dates()
		history_per_member, history_category_info, history_category_flags = self.get_card_history_per_member()
		for member, history_data in history_per_member.items():
			for category_tag, history_info in history_category_info.items():
				self.render_and_save("history_stats.html", f"pages/history/history_{member.first_name.lower()}_{category_tag}.html", {
					'member'         : member,
					'history_data'   : history_data[category_tag],
					'history_info'   : history_category_info[category_tag],
					'history_flags'  : history_category_flags[category_tag],
					'member_added'   : member_addition_dates,
				}, minify_html=not self.args.dev)
		return True

	def get_card_history_per_member(self):
		history_categories = {
			'all'        : ([Rarity.UR, Rarity.SR], None, ),
			'event'      : (Rarity.UR, [Source.Event]),
			'festival'   : (Rarity.UR, [Source.Festival]),
			'party'      : (Rarity.UR, [Source.Party]),
			'limited'    : (Rarity.UR, [Source.Festival, Source.Party]),
			'nonlimited' : (Rarity.UR, [Source.Unspecified, Source.Gacha, Source.Spotlight,]),
			'gacha'      : (Rarity.UR, [Source.Unspecified, Source.Gacha, Source.Spotlight, Source.Festival, Source.Party]),
			'ur'         : (Rarity.UR, None),
			'sr'         : (Rarity.SR, None),
		}
		category_info = {
			'all'        : ( "All",                  "History of any card, free or otherwise." ),
			'event'      : ( "Event UR",             "History of Event URs awarded in item exchange and story events." ),
			'festival'   : ( "Festival UR",          "History of Festival limited URs scouted exclusively from All Stars Festival banners." ),
			'party'      : ( "Party UR",             "History of Party limited URs scouted exclusively from Party Scouting banners." ),
			'limited'    : ( "Limited UR",           "History of all Festival and Party limited URs." ),
			'nonlimited' : ( "Non-Limited Gacha UR", "History of any non-limited UR scouted from banners using Star Gems." ),
			'gacha'      : ( "Any Gacha UR",         "History of any UR scouted from banners using Star Gems." ),
			'ur'         : ( "Any UR",               "History of any most recent UR, free or otherwise." ),
			'sr'         : ( "Any SR",               "History of any most recent SR, free or otherwise." ),
		}
		
		category_flags = {}
		for category, (rarity, sources) in history_categories.items(): 
			category_flags[category] = {
				'show_source'     : (not isinstance(sources, list) or len(sources) > 1),
				'show_rarity'     : (isinstance(rarity, list) and len(rarity) > 1),
			}
		
		history_by_member = {}
		
		now = datetime.now(timezone.utc)
		
		for member in Idols.all_idols:
			history_by_member[member.member_id] = self.client.get_idol_history(member.member_id, history_categories, now)
		
		return (history_by_member, category_info, category_flags)
		
