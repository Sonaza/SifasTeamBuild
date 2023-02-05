from IdolDatabase import *
from CardThumbnails import CardThumbnails
from CardValidity import *
from Utility import Utility

from ResourceProcessor import *
from PageRenderer import *

import platform
import argparse
import os
import time
from glob import glob
from operator import itemgetter
from collections import defaultdict, namedtuple
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

from colorama import init as colorama_init
from colorama import Fore, Style

from dataclasses import dataclass

@dataclass
class IdolElapsed:
	member    : Member
	idol      : KiraraIdol
	elapsed   : timedelta
	highlight : bool
	
	def __iter__(self):
		return iter((self.member, self.idol, self.elapsed, self.highlight))

class CardRotations():
	OutputDirectory = "public"
	
	def __init__(self):
		self.parser = argparse.ArgumentParser(description='Make some card rotations.')
		
		self.parser.add_argument("-f", "--force", help="Force database update regardless of when it was last performed.",
							action="store_true")
		
		self.parser.add_argument("-fr", "--force-render", help="Force render of all templates regardless if they've changed (database update not forced).",
							action="store_true")
		
		self.parser.add_argument("-ra", "--remake-atlas", help="Remake the atlas of thumbnails and the associated CSS code.",
							action="store_true")
		
		self.parser.add_argument("-a", "--auto", help="Flags this update as having been done automatically.",
							action="store_true")
		
		self.parser.add_argument("-dev", help="Flags it as developing build.",
							action="store_true")
		
		self.parser.add_argument("-w", "--watch", help="Instead of building anything start watching for asset changes and rebuild if things are modified.",
							action="store_true")
		
		self.parser.add_argument("--colored-output", help="Set log output to use colors. Values: 0 = off, 1 = on. Default: on.",
							action="store", metavar='ENABLED', type=int, default=1)
		
		self.args = self.parser.parse_args()
		
		self.css_settings = dotdict({
			'watch_directory' : "assets/",
			'watched_files'   : [
				"assets/css/*.css",
				"assets/css/*.scss",
			],
			'input_files'     : [
				"public/css/fonts.css",
				"assets/css/atlas.css",
				"assets/css/idols.css",
				"assets/css/style.scss",
				"assets/css/style-darkmode.scss",
				"assets/css/style-mobile.scss",
				"assets/css/style-darkmode-mobile.scss",
			],
			'output_file'     : os.path.join(self.OutputDirectory, "css/public.min.css").replace('\\', '/'),
		})
	
	def initialize(self):
		self.processor = ResourceProcessor(self)
		if self.args.watch:
			self.processor.watch_changes()
			exit()
			
		if not os.path.exists("assets/css/idols.css"):
			raise Exception("Generated idols.css does not exist! Run tools/generate_idols_css.py")
		
		if self.args.dev:
			print("------ BUILDING IN DEV MODE ------")
		else:
			print("------ BUILDING IN PROD MODE ------")
		print("Python version", platform.python_version())
		
		try:
			print("Current user id", os.getuid())
		except:
			pass
		print("Current Working Directory", os.getcwd())
		print()
		
		self.client = KiraraClient()
		self.client.update_database(forced=self.args.force)
		
		self.renderer = PageRenderer(self)
		if not self.renderer.render_history_loaded_successfully():
			print("Render history load failed, a full render is required!")
			self.args.force_render = True
			
		if not os.path.exists("public/js/tooltip_data.js"):
			print("Tooltip data file does not exist, a full render is required!")
			self.args.force_render = True
		
		if not os.path.exists("assets/css/atlas.css"):
			print("Atlas CSS does not exist and must be regenerated!")
			self.args.remake_atlas = True
		
		self.thumbnails = CardThumbnails(self.client, CardRotations.OutputDirectory)
		if not self.thumbnails.metadata_loaded_successfully():
			print("Atlas metadata does not exist or is corrupted and must be regenerated!")
			self.args.remake_atlas = True
		
		if self.thumbnails.download_thumbnails() or self.args.remake_atlas:
			self.thumbnails.make_atlas()
			self.args.force_render = True
		
		self.due_for_rendering_cache = {}
		
	# -------------------------------------------------------------------------------------------
	
	def _sort_rotation(self, rotation, order):
		output = []
		for ordered_member_id in order:
			if ordered_member_id in rotation:
				output.append((ordered_member_id, rotation[ordered_member_id]))
		
		return output
	
	# -------------------------------------------------------------------------------------------
	
	def get_attribute_type_array(self, group : Group):
		cards_per_girl = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
		
		for member in Idols.by_group[group]:
			for type in Type:
				if type == Type.Unset: continue
				for attribute in Attribute:
					if attribute == Attribute.Unset: continue
					cards_per_girl[member][type][attribute] = list()
			
		num_pages = 0
		for idol in self.client.get_idols_by_group(group, Rarity.UR):
			cards_per_girl[idol.member_id][idol.type][idol.attribute].append(idol)
			num_pages = max(num_pages, len(cards_per_girl[idol.member_id][idol.type][idol.attribute]))
		
		order = Idols.member_order_by_group[group]
		if group == Group.Nijigasaki:
			order = [
				Member.Rina,     Member.Kasumi,  Member.Shizuku, 
				Member.Ayumu,    Member.Setsuna, Member.Ai,      
				Member.Emma,     Member.Kanata,  Member.Karin,   
				Member.Shioriko, Member.Lanzhu,  Member.Mia,
			]
		
		arrays_sorted = self._sort_rotation(cards_per_girl, order)
		return (num_pages, arrays_sorted)
	
	# -------------------------------------------------------------------------------------------
	
	def get_general_rotation(self, group : Group, rarity : Rarity):
		from RotationsData.General import member_delays_by_rarity, set_title_overrides
		
		cards_per_girl = defaultdict(list)

		default_group_list = dict()
		for idol in Idols.by_group[group]:
			default_group_list[idol.member_id] = None
			
			if idol.member_id in member_delays_by_rarity[rarity]:
				if isinstance(member_delays_by_rarity[rarity][idol.member_id], int):
					cards_per_girl[idol.member_id].extend([CardNonExtant()] * member_delays_by_rarity[rarity][idol.member_id])
				else:
					cards_per_girl[idol.member_id].extend([CardNonExtant()] * member_delays_by_rarity[rarity][idol.member_id][0])
					member_delays_by_rarity[rarity][idol.member_id] = member_delays_by_rarity[rarity][idol.member_id][1:]
					

		idols = self.client.get_idols_by_group(group, rarity)
		for idol in idols:
			cards_per_girl[idol.member_id].append(idol)
			
			if idol.member_id in member_delays_by_rarity[rarity]:
				if isinstance(member_delays_by_rarity[rarity][idol.member_id], list) and len(member_delays_by_rarity[rarity][idol.member_id]) > 0:
					cards_per_girl[idol.member_id].extend([CardNonExtant()] * member_delays_by_rarity[rarity][idol.member_id][0])
					member_delays_by_rarity[rarity][idol.member_id] = member_delays_by_rarity[rarity][idol.member_id][1:]
			
		num_rotations = 0
		for member_id, cards in cards_per_girl.items():
			num_rotations = max(num_rotations, len(cards))

		rotations = []
		for rotation_index in range(num_rotations):
			current_rotation = dict(default_group_list)
			
			try:
				set_title = set_title_overrides[rarity][group][rotation_index]
			except KeyError:
				set_title = None
			
			titles = defaultdict(int)
			
			for idol in Idols.by_group[group]:
				if idol.member_id not in cards_per_girl:
					current_rotation[idol.member_id] = CardMissing()
				else:
					cards = cards_per_girl[idol.member_id]
					if rotation_index < len(cards):
						current_rotation[idol.member_id] = cards[rotation_index]
						
						if set_title == None and rarity == Rarity.SR and is_valid_card(cards[rotation_index]):
							t = cards[rotation_index].get_card_name(True)
							titles[t] += 1
					else:
						current_rotation[idol.member_id] = CardMissing()
			
			if titles:
				titles = sorted(titles.items(), key=itemgetter(1), reverse=True)
				if len(titles) == 1 or titles[0][1] > 1:
					set_title = titles[0][0]
				else:
					print("WARNING! No set name could be determined for", rarity, group, "index", rotation_index)
		
			rotations.append(( self._sort_rotation(current_rotation, Idols.member_order_by_group[group]), set_title ))
			rotation_index += 1
		
		return rotations
	
	# -------------------------------------------------------------------------------------------
	
	def get_sr_sets(self, group : Group):
		from RotationsData.SRSets import skipped_sets, idolized_same_set
		
		try:
			skipped_sets = skipped_sets[group]
		except:
			skipped_sets = {}
		try:
			idolized_same_set = dict([(title.strip(), set_title) for set_title, idolized_titles in idolized_same_set[group].items() for title in idolized_titles])
		except:
			idolized_same_set = {}
		
		current_set_index = 0
		set_indexes = []
		idol_sets = defaultdict(dict)
		
		idols = self.client.get_idols_by_group(group, Rarity.SR)
		for idol in idols:
			title = idol.get_card_name(True)
			try:
				title = idolized_same_set[title]
			except:
				pass
			
			if title not in idol_sets:
				# print(title.encode('utf-8'))
				set_indexes.append((current_set_index, title))
				current_set_index += 1
			
			idol_sets[title][idol.member_id] = idol
		
		rotations = []
		for index, set_title in set_indexes:
			current_rotation = {}
			for member in Idols.member_order_by_group[group]:
				if member in idol_sets[set_title]:
					# Card found, add to rotation
					current_rotation[member] = idol_sets[set_title][member]
					
				elif member in skipped_sets and index in skipped_sets[member]:
					# Card is explicitly skipped
					current_rotation[member] = CardNonExtant()
					
				else:
					# Card not yet added to the game
					current_rotation[member] = CardMissing()
			
			rotations.append(( self._sort_rotation(current_rotation, Idols.member_order_by_group[group]), set_title ))
		
		return rotations
	
	# -------------------------------------------------------------------------------------------
	
	def get_source_rotation(self, group : Group, source : Source):
		from RotationsData.General import member_delays_by_source
		
		cards_per_girl = defaultdict(list)

		default_group_list = dict()
		for idol in Idols.by_group[group]:
			default_group_list[idol.member_id] = None
			
			try:
				cards_per_girl[idol.member_id].extend([CardNonExtant()] * member_delays_by_source[source][idol.member_id])
			except KeyError:
				pass

		idols = self.client.get_idols(group=group, rarity=Rarity.UR, source=source)
		for idol in idols:
			cards_per_girl[idol.member_id].append(idol)
			
		num_rotations = 0
		for member_id, cards in cards_per_girl.items():
			num_rotations = max(num_rotations, len(cards))

		rotations = []
		for rotation_index in range(num_rotations):
			current_rotation = dict(default_group_list)
			
			for idol in Idols.by_group[group]:
				if idol.member_id not in cards_per_girl:
					current_rotation[idol.member_id] = CardMissing()
				else:
					cards = cards_per_girl[idol.member_id]
					if rotation_index < len(cards):
						current_rotation[idol.member_id] = cards[rotation_index]
					else:
						current_rotation[idol.member_id] = CardMissing()
			
			rotations.append(( self._sort_rotation(current_rotation, Idols.member_order_by_group[group]), None ))
			rotation_index += 1
		
		return rotations
		
	# -------------------------------------------------------------------------------------------
	
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
	
	# ------------------------------------------------
		
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
		
	# ------------------------------------------------
	
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
			elapsed_list.insert(0, IdolElapsed(member_id, CardNonExtant(), 0, False))
			
		return elapsed_list, has_empty_rows
		
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
			'limited'    : ( "Limited UR",           "The most recent Festival and Party limited URs. Due to their higher average power level and limited nature, the same member is unlikely to receive two in quick succession." ),
			'spotlight'  : ( "Party + Spotlight UR", "Party banners replaced Spotlight banners upon their introduction and release order up until now has followed in its footsteps." ),
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
				category_data[category][group] = {
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
	
	# -------------------------------------------------------------------------------------------
	
	def get_events_with_cards(self):
		events = self.client.get_events_with_cards()
		features = self.client.get_event_features_per_member()
		
		zero_feature_members = [member for member, num_features in features.items() if num_features == 0]
		
		sbl_reference_point = {
			'event_id' : 47,
			'date'     : datetime(year=2022, month=9, day=1),
		}
		today = datetime.today()
		while sbl_reference_point['date'].month != today.month or sbl_reference_point['date'].year != today.year:
			if (sbl_reference_point['event_id'] + 1) not in events:
				break

			sbl_reference_point['event_id'] += 1
			sbl_reference_point['date'] += relativedelta(months=1)
		
		events_per_month = 1
		diff_bonus = 0
		for event_id, data in events.items():
			# if event_id == 49:
			# 	events_per_month = 1
			# 	diff_bonus = 14
			
			data['idols'] = []
			data['idols'].append(f"featured-idol-{data['free'][0].member_id.value}")
			
			for idol in data['free'] + data['gacha']:
				data['idols'].append(f"has-idol-{idol.member_id.value}")
			data['idols'] = ' '.join(data['idols'])
			
			if event_id <= sbl_reference_point['event_id']:
				continue
			
			diff = ((event_id - sbl_reference_point['event_id']) - 1) // events_per_month + 1 - diff_bonus
			estimated_addition = sbl_reference_point['date'] + relativedelta(months=diff)
			data['sbl'] = estimated_addition.strftime('%b %Y')
		
		return events, zero_feature_members
	
	# -------------------------------------------------------------------------------------------
	
	def get_banners_with_cards(self):
		banners = self.client.get_banners_with_cards()
		
		banner_title_overrides = dict([
			(21, "Initial SR Shioriko (Nijigasaki Festival)"),
			(48, "Initial SR Mia and Lanzhu"),
		])
		
		for banner_id, data in banners.items():
			featured_members = []
			num_urs = sum([1 if card.rarity == Rarity.UR else 0 for card in data['cards']])
			
			data['idols'] = []
			for idol in data['cards']:
				data['idols'].append(f"has-idol-{idol.member_id.value}")
				
				if num_urs == 0 or idol.rarity == Rarity.UR:
					featured_members.append(idol.member_id.first_name)
				
			data['idols'] = ' '.join(data['idols'])
			
			featured_str = ', '.join(featured_members)
			featured_str = ' and '.join(featured_str.rsplit(', ', 1))
			
			if banner_id in banner_title_overrides:
				data['banner']['title'] = banner_title_overrides[banner_id]
			
			else:
				if data['banner']['type'] == BannerType.Spotlight:
					data['banner']['title'] = f"{data['banner']['type'].name} {featured_str}"
				else:
					data['banner']['title'] = f"{Utility.ordinalize(data['index'] + 1)} {data['banner']['type'].name} {featured_str}"
		
		return banners
	
	# -------------------------------------------------------------------------------------------
	
	def _get_preload_assets(self):
		preload_assets = []
		preload_asset_files = [
			self.css_settings.output_file,
			os.path.join(CardRotations.OutputDirectory, "js/public.js"),
			os.path.join(CardRotations.OutputDirectory, "js/tooltip_data.js"),
		]
		preload_asset_files.extend(glob(os.path.join(CardRotations.OutputDirectory, "img/thumbnails/atlas_*_30_*_idolized.webp")))
		
		ext_types = {
			'.css'  : 'style',
			'.png'  : 'image',
			'.webp' : 'image',
			'.js'   : 'script',
		}
		
		for filepath in preload_asset_files:
			rel = 'preload'
			
			filepath = filepath.replace('\\', '/')
			filehash = Utility.get_file_modifyhash(filepath)
			
			relative_path = filepath.replace('public/', '')
			base, ext = os.path.splitext(relative_path)
			
			preload_assets.append({
				'path'   : f"/{base}.{filehash}{ext}",
				'type'   : ext_types[ext],
				'rel'    : rel,
			})
		
		return preload_assets
	
	def is_doing_full_render(self):
		return self.args.force or self.args.force_render or self.client.was_database_updated()
		
	def due_for_rendering(self, template_filename):
		if self.is_doing_full_render():
			return True
		
		def check(self, template_filename):
			if self.renderer.has_template_changed(template_filename) or self.renderer.is_any_output_missing(template_filename):
				self.renderer.reset_output(template_filename)
				return True
			self.renderer.preserve_output(template_filename)
			return False
		
		if template_filename not in self.due_for_rendering_cache:
			self.due_for_rendering_cache[template_filename] = check(self, template_filename)
		return self.due_for_rendering_cache[template_filename]
	
	# --------------------------------------------
	
	def testing_stuff(self):
		results = {
			Source.Festival: {},
			Source.Party: {},
		}
		offsets = []
		
		for day in range(0, 21):
			offset = day - 10
			offsets.append(offset)
			
			result = self.client.get_weighted_overdueness(days_offset=offset)
			for source, overdueness in result.items():
				for member, data in overdueness.items():
					if member not in results[source]:
						results[source][member] = []
					results[source][member].append(data['weighted_value'])
		
		print(f"{'Member':<10}\t", end='')
		for offset in offsets:
			print(f"{offset:>7}\t", end='')
		print()
			
		for source, data in results.items():
			for member, values in data.items():
				print(f"{member.first_name:<10}\t", end='')
				for value in values:
					print(f"{value:>7.2f}\t", end='')
				print()
			print()
			
		return True
	
	# --------------------------------------------
	
	def generate_pages(self):
		files_to_delete = [x.replace("\\", "/") for x in glob(os.path.join(CardRotations.OutputDirectory, "pages/*.html"))]
		files_to_delete.extend([x.replace("\\", "/") for x in glob(os.path.join(CardRotations.OutputDirectory, "pages/history/*.html"))])
		files_to_delete.extend([x.replace("\\", "/") for x in glob(os.path.join(CardRotations.OutputDirectory, "pages/deferred/*.html"))])
		
		render_start_time = time.perf_counter()
		render_unique_str = str(hash(time.time()))[2:8]
		
		# -------------------------------------------------------
		# Per school UR attribute-type arrays
		
		if self.due_for_rendering("attribute_type_array.html"):
			idol_arrays = [(group, *self.get_attribute_type_array(group)) for group in Group]
			for data in idol_arrays:
				output_file = self.renderer.render_and_save("attribute_type_array.html", f"pages/idol_arrays_{data[0].tag}.html", {
					'idol_arrays'        : [ data ],
				}, minify=not self.args.dev)
		
		# -------------------------------------------------------
		# Basic rotations
		
		if any([self.due_for_rendering("deferred_rotation.html"), self.due_for_rendering("deferred_card_grid.html")]):
			def render_deferred_card_grids(rotation_set_label, grouped_rotations, unique_str):
				for group, group_data in grouped_rotations:
					for index, (card_rotation, rotation_title) in enumerate(group_data):
						self.renderer.render_and_save("deferred_card_grid.html", f"pages/deferred/{rotation_set_label}_{group.tag}_{index + 1}.html", {
							'card_rotation'      : card_rotation,
						}, minify=not self.args.dev)
			
			# General UR rotations
			ur_rotations = [(group, self.get_general_rotation(group, Rarity.UR)) for group in Group]
			self.renderer.render_and_save("deferred_rotation.html", "pages/ur_rotations.html", {
				'grouped_rotations'  : ur_rotations,
				'rotation_set_label' : 'ur',
				'render_unique_str'  : render_unique_str,
				'set_label'          : 'Rotation',
				'page_title'         : 'UR Rotations',
				'page_description'   : '''Rotations for all UR cards. <b>Please note:</b> these rotations are automatically laid in the original release
				                          order and manual per-rotation exceptions are not planned for this page beyond adjusting the initial URs.''',
			}, minify=not self.args.dev)
			render_deferred_card_grids('ur', ur_rotations, render_unique_str)
		
			# Festival UR rotations
			festival_rotations = [(group, self.get_source_rotation(group, Source.Festival)) for group in Group]
			self.renderer.render_and_save("deferred_rotation.html", "pages/festival_rotations.html", {
				'grouped_rotations'  : festival_rotations,
				'rotation_set_label' : 'festival',
				'render_unique_str'  : render_unique_str,
				'set_label'          : 'Rotation',
				'page_title'         : 'Festival UR Rotations',
				'page_description'   : 'Rotations for Festival limited URs scouted exclusively from All Stars Festival banners.',
			}, minify=not self.args.dev)
			render_deferred_card_grids('festival', festival_rotations, render_unique_str)
		
			# Party UR rotations
			party_rotations = [(group, self.get_source_rotation(group, Source.Party)) for group in Group]
			self.renderer.render_and_save("deferred_rotation.html", "pages/party_rotations.html", {
				'grouped_rotations'  : party_rotations,
				'rotation_set_label' : 'party',
				'render_unique_str'  : render_unique_str,
				'set_label'          : 'Rotation',
				'page_title'         : 'Party UR Rotations',
				'page_description'   : 'Rotations for Party limited URs scouted exclusively from Party Scouting banners.',
			}, minify=not self.args.dev)
			render_deferred_card_grids('party', party_rotations, render_unique_str)
		
			# Event UR rotations
			event_rotations = [(group, self.get_source_rotation(group, Source.Event)) for group in Group]
			self.renderer.render_and_save("deferred_rotation.html", "pages/event_rotations.html", {
				'grouped_rotations'  : event_rotations,
				'rotation_set_label' : 'event',
				'render_unique_str'  : render_unique_str,
				'set_label'          : 'Rotation',
				'page_title'         : 'Event UR Rotations',
				'page_description'   : 'Rotations for Event URs awarded in item exchange and story events.',
			}, minify=not self.args.dev)
			render_deferred_card_grids('event', event_rotations, render_unique_str)
		
			# SR Sets
			sr_sets = [(group, self.get_sr_sets(group)) for group in Group]
			self.renderer.render_and_save("deferred_rotation.html", "pages/sr_sets.html", {
				'grouped_rotations'  : sr_sets,
				'rotation_set_label' : 'sr',
				'render_unique_str'  : render_unique_str,
				'set_label'          : 'Set',
				'page_title'         : 'SR Sets',
				'page_description'   : '''SR cards organised into sets by costume or other common theme.''',
			}, minify=not self.args.dev)
			render_deferred_card_grids('sr', sr_sets, render_unique_str)
		
		# -------------------------------------------------------
		# Event cards info
		
		if any([self.due_for_rendering("event_cards_deferred.html"), self.due_for_rendering("event_cards_deferred_row.html")]):
			events_with_cards, zero_feature_members = self.get_events_with_cards()
			for event_index, (event_id, event_data) in enumerate(events_with_cards.items()):
				self.renderer.render_and_save("event_cards_deferred_row.html", f"pages/deferred/event_cards_{event_id}.html", {
					'event_id'        : event_id,
					'event_data'      : event_data,
					'event_row_index' : event_index + 1,
				}, minify=not self.args.dev)
			
			self.renderer.render_and_save("event_cards_deferred.html", "pages/event_cards.html", {
				'events_with_cards'    : events_with_cards,
				'zero_feature_members' : zero_feature_members,
			}, minify=not self.args.dev)
			
		# -------------------------------------------------------
		# Banner info
		
		if any([self.due_for_rendering("banners_deferred.html"), self.due_for_rendering("banners_deferred_row.html")]):
			banners_with_cards = self.get_banners_with_cards()
			for banner_index, (banner_id, banner_data) in enumerate(banners_with_cards.items()):
				self.renderer.render_and_save("banners_deferred_row.html", f"pages/deferred/banner_{banner_id}.html", {
					'banner_id'        : banner_id,
					'banner_data'      : banner_data,
					'banner_row_index' : banner_index + 1,
				}, minify=not self.args.dev)
				
			self.renderer.render_and_save("banners_deferred.html", "pages/banners.html", {
				'banners_with_cards' : banners_with_cards,
			}, minify=not self.args.dev)
		
		# -------------------------------------------------------
		# Card history
		
		history_category = {
			Source.Unspecified : 'gacha',
			Source.Event       : 'event',
			Source.Gacha       : 'gacha',
			Source.Spotlight   : 'gacha',
			Source.Festival    : 'festival',
			Source.Party       : 'party',
		}
		
		if self.due_for_rendering("history_frontpage.html"):
			self.renderer.render_and_save("history_frontpage.html", "pages/history.html", {}, minify=not self.args.dev)
		
		if self.due_for_rendering("history_stats.html"):
			member_addition_dates = self.client.get_member_addition_dates()
			
			history_per_member, history_category_info, history_category_flags = self.get_card_history_per_member()
			for member, history_data in history_per_member.items():
				for category_tag, history_info in history_category_info.items():
					self.renderer.render_and_save("history_stats.html", f"pages/history/history_{member.first_name.lower()}_{category_tag}.html", {
						'member'         : member,
						'history_data'   : history_data[category_tag],
						'history_info'   : history_category_info[category_tag],
						'history_flags'  : history_category_flags[category_tag],
						'member_added'   : member_addition_dates,
					}, minify=not self.args.dev)
			
		# -------------------------------------------------------
		# Card stats
		
		if self.due_for_rendering("stats.html"):
			general_stats, maximums = self.client.get_general_stats()
			self.renderer.render_and_save("stats.html", "pages/stats.html", {
				'category_tag'   : 'general',
				'general_stats'  : general_stats,
			}, minify=not self.args.dev)
			
			card_stats, category_info, category_has_empty_rows = self.get_card_stats()
			for category_tag in card_stats.keys():
				self.renderer.render_and_save("stats.html", f"pages/stats_{category_tag}.html", {
					'category_tag'     : category_tag,
					'category_data'    : card_stats[category_tag],
					'category_info'    : category_info[category_tag],
					'has_empty_rows'   : category_has_empty_rows[category_tag],
					'history_category' : history_category,
				}, minify=not self.args.dev)
		
		if self.due_for_rendering("weighted_overdueness.html"):
			weighted_overdueness = self.client.get_weighted_overdueness()
			self.renderer.render_and_save("weighted_overdueness.html", f"pages/stats_overdueness.html", {
				'weighted_overdueness' : weighted_overdueness,
				'history_category'     : history_category,
			}, minify=not self.args.dev)
		
		# -------------------------------------------------------
		# Index page
		
		if self.due_for_rendering("home.html"):
			self.renderer.render_and_save("home.html", "pages/home.html", {}, minify=not self.args.dev)
		
		# -------------------------------------------------------
		# Compile and minify CSS
		
		self.processor.compile_css(
			input_files = self.css_settings.input_files,
			output_file = self.css_settings.output_file,
			minify=not self.args.dev,
		)
		
        # -------------------------------------------------------
		# Error Pages
		
		if self.due_for_rendering("error.html"):
			self.renderer.render_and_save("error.html", "error/400.html", {
				'error_code'   : 400,
				'error_status' : 'Bad Request',
				'error_text'   : "The server is unable to handle the malformed request made by your browser.",
			}, minify=True)
			
			self.renderer.render_and_save("error.html", "error/403.html", {
				'error_code'   : 403,
				'error_status' : 'Forbidden',
				'error_text'   : "You are not permitted to access this resource. Move along, citizen.",
			}, minify=True)
			
			self.renderer.render_and_save("error.html", "error/404.html", {
				'error_code'   : 404,
				'error_status' : 'Not Found',
				'error_text'   : "Whoopsie! Whatever it is you're looking for at this URL does not exist.<br><br>If a page links here directly or you think something should have been here please send feedback.",
			}, minify=True)
			
			self.renderer.render_and_save("error.html", "error/410.html", {
				'error_code'   : 410,
				'error_status' : 'Gone',
				'error_text'   : "Whoopsie! Whatever it is you're looking for at this URL is permanently gone.",
			}, minify=True)
			
			self.renderer.render_and_save("error.html", "error/500.html", {
				'error_code'   : 500,
				'error_status' : 'Server Error',
				'error_text'   : "The server encountered an unrecoverable error while processing your request.<br><br>Please try again later.",
			}, minify=True)
			
			self.renderer.render_and_save("error.html", "error/503.html", {
				'error_code'   : 503,
				'error_status' : 'Unavailable',
				'error_text'   : "Service is temporarily unavailable. Please try again later.",
			}, minify=True)
		
		# -------------------------------------------------------
		# Crawler Info
		
		if self.due_for_rendering("crawler.html"):
			self.renderer.render_and_save("crawler.html", "crawler.html", {}, minify=True)
		
		# -------------------------------------------------------
		# .htaccess
		
		preload_assets = self._get_preload_assets()
		if self.due_for_rendering("template.htaccess"):
			self.renderer.render_and_save("template.htaccess", ".htaccess", {
				'preloads' : preload_assets
			}, minify=False, generated_note=True)
		
		# -------------------------------------------------------
		# Main index and layout
		
		if self.is_doing_full_render():
			self.renderer.save_tooltip_data("js/tooltip_data.js")
		
		render_time_so_far = time.perf_counter() - render_start_time
		
		last_data_update = self.client.get_database_update_time()
		now = datetime.now(timezone.utc)
		self.renderer.render_and_save("main_layout.php", "views/content_index.php", {
			'last_update'      : now,
			'last_data_update' : last_data_update,
			'render_time'      : f"{render_time_so_far:0.2f}s",
			'preloads'         : preload_assets,
		}, minify=False, output_basepath='')
		
		# -------------------------------------------------------
		# File cleanup
		
		self.renderer.save_render_history()
		
		for file in files_to_delete:
			if file in self.renderer.rendered_pages: continue
			
			print(f"Removing outdated file  {file}")
			os.remove(file)
		
		render_time_total = time.perf_counter() - render_start_time
		print(f"\nAll done! Rendering took {render_time_total:0.3f}s\n")

# -------------------------------------------------------------------------------------------

if __name__ == "__main__":
	cr = CardRotations()
	colored_output = (cr.args.colored_output == 1)
	# print("Using colored output", colored_output)
	
	# Only strip on windows for Sublime Text, somehow it still displays in console?
	colorama_init(autoreset=True, strip=not colored_output)
	
	buildstatus = {
		"timestamp" : datetime.now(timezone.utc).isoformat(),
		"handled"   : None,
		"auto"      : cr.args.auto,
		"forced"    : cr.args.force,
		"success"   : None,
		"message"   : "",
	}
	build_exception = None
	
	cr.initialize()
	
	# if cr.testing_stuff(): exit()
	
	try:
		cr.generate_pages()
		buildstatus['success'] = True
		buildstatus['message'] = "All OK!"
		
	except Exception as e:
		buildstatus['success'] = False
		
		import traceback
		buildstatus['message'] = traceback.format_exc()
		
		build_exception = e
	
	output_file = open("build.status", "w")
	json.dump(buildstatus, output_file)
	output_file.close()
	
	if not buildstatus['success']:
		raise build_exception
	
	print()
