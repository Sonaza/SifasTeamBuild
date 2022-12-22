from IdolDatabase import *
from CardThumbnails import CardThumbnails
from CardValidity import *

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
from colorama import Fore
from colorama import Style

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
			
		self.renderer = PageRenderer(self)
		
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
		
		print()
		
		if not os.path.exists("assets/css/idols.css"):
			raise Exception("Generated idols.css does not exist! Run tools/generate_idols_css.py")
		
		if not os.path.exists("assets/css/atlas.css"):
			print("Atlas CSS file does not exist and must be regenerated!")
			self.args.remake_atlas = True
		
		self.thumbnails = CardThumbnails(self.client, CardRotations.OutputDirectory)
		if self.thumbnails.download_thumbnails() or self.args.remake_atlas:
			self.thumbnails.make_atlas()
		
	# -------------------------------------------------------------------------------------------
	
	def _sort_rotation(self, group, rotation, order):
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
		
		arrays_sorted = self._sort_rotation(group, cards_per_girl, order)
		return (num_pages, arrays_sorted)
	
	def get_general_rotation(self, group : Group, rarity : Rarity):
		member_delays = {
			Rarity.SR : {
				Member.Shioriko : [0, 3, 2, ],
				Member.Lanzhu   : [0, 8, ],
				Member.Mia      : [0, 8, ],
			},
			Rarity.UR : {
				Member.Shioriko : 3,
				Member.Lanzhu   : 7,
				Member.Mia      : 7,
			},
		}
		
		set_title_overrides = {
			Rarity.SR : {
				Group.Nijigasaki : dict([
					(0,  "1st Nijigasaki Solo"),
					(5,  "3rd Nijigasaki Solo"),
					(10, "Rainbow Waltz"),
				])
			}
		}
		
		cards_per_girl = defaultdict(list)

		default_group_list = dict()
		for idol in Idols.by_group[group]:
			default_group_list[idol.member_id] = None
			
			if idol.member_id in member_delays[rarity]:
				if isinstance(member_delays[rarity][idol.member_id], int):
					cards_per_girl[idol.member_id].extend([CardNonExtant()] * member_delays[rarity][idol.member_id])
				else:
					cards_per_girl[idol.member_id].extend([CardNonExtant()] * member_delays[rarity][idol.member_id][0])
					member_delays[rarity][idol.member_id] = member_delays[rarity][idol.member_id][1:]
					

		idols = self.client.get_idols_by_group(group, rarity)
		for idol in idols:
			cards_per_girl[idol.member_id].append(idol)
			
			if idol.member_id in member_delays[rarity]:
				if isinstance(member_delays[rarity][idol.member_id], list) and len(member_delays[rarity][idol.member_id]) > 0:
					cards_per_girl[idol.member_id].extend([CardNonExtant()] * member_delays[rarity][idol.member_id][0])
					member_delays[rarity][idol.member_id] = member_delays[rarity][idol.member_id][1:]
			
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
		
			rotations.append(( self._sort_rotation(group, current_rotation, Idols.member_order_by_group[group]), set_title ))
			rotation_index += 1
		
		return rotations
	
	# -------------------------------------------------------------------------------------------
	
	def get_sr_sets(self, group : Group):
		skipped_sets = {
			Group.Nijigasaki : {
				Member.Rina     : [11, ],
				Member.Kasumi   : [11, ],
				Member.Shizuku  : [11, ],
				Member.Ayumu    : [11, ],
				Member.Setsuna  : [11, ],
				Member.Ai       : [11, ],
				Member.Emma     : [11, ],
				Member.Kanata   : [11, ],
				Member.Karin    : [11, ],
				Member.Shioriko : [1, 2, 3, 5, 6, 13, ],
				Member.Lanzhu   : [1, 2, 3, 4, 5, 6, 7, 8, 13, ],
				Member.Mia      : [1, 2, 3, 4, 5, 6, 7, 8, 13, ],
			}
		}
		try:
			skipped_sets = skipped_sets[group]
		except:
			skipped_sets = {}
		
		idolized_same_set = {
			Group.Muse : {
				'A song for You! You? You!!': [
					'A Song for You! You? You!',
					'A song for You! You? You!!',
				],
				
				'Mermaid Festa Vol.1' : [
					'Mermaid festa vol.1',
				],
			},
			
			Group.Nijigasaki : {
				'1st Nijigasaki Solo' : [
					'Yume e no Ippo',
					'Diamond',
					'Anata no Risou no Heroine',
					'Starlight',
					'Meccha Going!!',
					'Nemureru Mori ni Ikitai na',
					'CHASE!',
					'Evergreen',
					'Dokipipo\u2606Emotion',
					'Ketsui no Hikari',
					'I\'m Still...',
					'Queendom',
				],
				
				'Exciting Animal' : ['Excited Animal'],
				
				# '2nd Niji Solo': [
				'R3BIRTH 2nd Solo': [
					'Kaika Sengen',
					'\u2606Wonderland\u2606',
					'Audrey',
					'Wish',
					'You & I',
					'My Own Fairy-Tale',
					'MELODY',
					'Koe Tsunagou yo',
					'Tele Telepathy',
					'Aoi Canaria',
					'Toy Doll',
					'Ye Mingzhu',
				],
				
				'3rd Nijigasaki Solo': [
					'Aion no Uta',
					'Marchen Star',
					'Say Good-Bye Namida',
					'Yagate Hitotsu no Monogatari',
					'Margaret',
					'Analog Heart',
					'Tanoshii no Tensai',
					'Fire Bird',
					'LIKE IT! LOVE IT!',
					'Concentrate!',
				],
				
				'4th Nijigasaki Solo': [
					'Break The System',
					'TO BE YOURSELF',
					'Eieisa',
					'Turn it Up!',
					'Diabolic mulier',
					'Silent Blaze',
					'Yada!',
					'Itsu datte for you!',
					'First Love Again',
				],
				
				'4th Nijigasaki Solo': [
					'Break The System',
					'TO BE YOURSELF',
					'Eieisa',
					'Turn it Up!',
					'Diabolic mulier',
					'Silent Blaze',
					'Yada!',
					'Itsu datte for you!',
					'First Love Again',
				],
				
				'Eien no Isshun': [
					'Eien no Issyun',
				],
			}
		}
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
			
			rotations.append(( self._sort_rotation(group, current_rotation, Idols.member_order_by_group[group]), set_title ))
		
		return rotations
	
	# -------------------------------------------------------------------------------------------
	
	def get_source_rotation(self, group : Group, source : Source):
		member_delays = {
			Source.Event : {
				Member.Shioriko : 1,
				Member.Lanzhu   : 1,
				Member.Mia      : 1,
			},
			Source.Festival : {
				Member.Shioriko : 0,
				Member.Lanzhu   : 2,
				Member.Mia      : 2,
			},
			Source.Party : {
				Member.Shioriko : 0,
				Member.Lanzhu   : 0,
				Member.Mia      : 0,
			},
		}
		
		cards_per_girl = defaultdict(list)

		default_group_list = dict()
		for idol in Idols.by_group[group]:
			default_group_list[idol.member_id] = None
			
			try:
				cards_per_girl[idol.member_id].extend([CardNonExtant()] * member_delays[source][idol.member_id])
			except KeyError:
				pass

		idols = self.client.get_idols(group=group, rarity=Rarity.UR, source=source)
		for idol in idols:
			cards_per_girl[idol.member_id].append(idol)
			
		num_rotations = 0
		for member_id, cards in cards_per_girl.items():
			# print(f"{Idols.by_member_id[member_id].first_name:>10} has {len(cards):>2} URs")
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
			
			rotations.append(( self._sort_rotation(group, current_rotation, Idols.member_order_by_group[group]), None ))
			rotation_index += 1
		
		return rotations
		
	# -------------------------------------------------------------------------------------------
	
	def _make_general_stats(self, group : Group):
		categories = ['SRs', 'URs', 'event', 'festival', 'party', 'gacha', ]
		stats = defaultdict(lambda: defaultdict(int))
		
		for idol in Idols.by_group[group]:
			for category in categories:
				stats[idol.member_id][category] = 0
			
			stats[idol.member_id]['attributes'] = defaultdict(int)
			stats[idol.member_id]['types'] = defaultdict(int)
		
		idols = self.client.get_idols(group=group)
		for idol in idols:
			if idol.rarity == Rarity.SR:
				stats[idol.member_id]['SRs'] += 1
				
			elif idol.rarity == Rarity.UR:
				stats[idol.member_id]['URs'] += 1
				
				if idol.source == Source.Event:
					stats[idol.member_id]['event'] += 1
					
				elif idol.source == Source.Festival:
					stats[idol.member_id]['festival'] += 1
					
				elif idol.source == Source.Party:
					stats[idol.member_id]['party'] += 1
					
				elif idol.source == Source.Gacha or idol.source == Source.Spotlight or idol.source == Source.Unspecified:
					stats[idol.member_id]['gacha'] += 1
				
				stats[idol.member_id]['attributes'][idol.attribute] += 1
				stats[idol.member_id]['types'][idol.type] += 1
		
		return self._sort_rotation(group, stats, Idols.member_order_by_group[group])
	
	def get_general_stats(self):
		stats = {}
		for group in Group:
			stats[group] = self._make_general_stats(group=group)
			
		return stats
	
	# -------------------------------------------------------------------------------------------
	
	def _time_since_last(self, idols, group=None):
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
		idols_timedata = []
		for idol in idols:
			duplicate = not (idol.member_id in all_idols)
			
			# member, card, time_since, highlight
			idols_timedata.append((idol.member_id, idol, now - idol.release_date, duplicate))
			
			if duplicate and idol.member_id not in highlighted_idols:
				highlighted_idols.add(idol.member_id)
				
			try:
				all_idols.remove(idol.member_id)
			except: pass
		
		# Highlight all duplicate idol entries
		for index, idol in enumerate(idols_timedata):
			if idol[0] in highlighted_idols:
				idols_timedata[index] = (idol[0], idol[1], idol[2], True)
		
		has_empty_rows = (len(all_idols) > 0)
		
		# Add dummy entries for idols not found in the dataset
		for member_id in all_idols:
			idols_timedata.insert(0, (member_id, CardNonExtant(), 0, False))
			
		return idols_timedata, has_empty_rows
	
	def get_newest_idols(self, group : Group = None, rarity : Rarity = None, source : Source = None):
		idols = self.client.get_newest_idols(group=group, rarity=rarity, source=source)
		
		now = datetime.now(tz=timezone.utc) - timedelta(hours=24)
		
		pending_members = []
		for idol in idols:
			if idol.release_date > now:
				pending_members.append(idol.member_id)
				
		if pending_members:
			previous_idols = self.client.get_newest_idols(group=group, rarity=rarity, source=source,
				members=pending_members, released_before=now)
			idols.extend(previous_idols)
			idols.sort(key=lambda x: x.release_date)
			
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
		limited_max_offsets = {
			Member.Mia    : { Source.Festival : -2, Source.Party : 0, },
			Member.Lanzhu : { Source.Festival : -2, Source.Party : 0, },
		}
		limited_idols, max_per_source = self.client.get_idols_by_source_and_member([Source.Festival, Source.Party])
		
		category_data = defaultdict(dict)
		category_has_empty_rows = defaultdict(bool)
		
		now = datetime.now(tz=timezone.utc)
		
		for category, (rarity, sources) in categories.items():
			for group in Group:
				time_since_list, has_empty_rows = self._time_since_last(idols=self.get_newest_idols(group=group, rarity=rarity, source=sources), group=group)
				category_data[category][group] = {
					'cards'           : time_since_list,
					'has_empty_rows'  : has_empty_rows,
					'show_source'     : (not isinstance(sources, list) or len(sources) > 1),
					'show_rarity'     : (isinstance(rarity, list) and len(rarity) > 1),
					'limited_idols'   : limited_idols,
					'limited_sources' : (limited_sources[category] if category in limited_sources else []),
					'max_per_source'  : max_per_source,
					'limited_max_offsets' : limited_max_offsets,
				}
				category_has_empty_rows[category] = has_empty_rows or category_has_empty_rows[category]
				
			time_since_list, has_empty_rows = self._time_since_last(idols=self.get_newest_idols(rarity=rarity, source=sources), group=None)
			category_data[category]['collapsed'] = {
				'cards'           : time_since_list,
				'has_empty_rows'  : has_empty_rows,
				'show_source'     : (not isinstance(sources, list) or len(sources) > 1),
				'show_rarity'     : (isinstance(rarity, list) and len(rarity) > 1),
				'limited_idols'   : limited_idols,
				'limited_sources' : (limited_sources[category] if category in limited_sources else []),
				'max_per_source'  : max_per_source,
				'limited_max_offsets' : limited_max_offsets,
			}
			category_has_empty_rows[category] = has_empty_rows or category_has_empty_rows[category]
		
		return (category_data, category_info, category_has_empty_rows)
	
	# -------------------------------------------------------------------------------------------
	
	def get_events_with_cards(self):
		events = self.client.get_events_with_cards()
		features = self.client.get_event_features_per_member()
		
		zero_feature_members = [member for member, num_features in features.items() if num_features == 0]
		
		# sbl_events = [{'title': 'Trial Event: SIFAS Big Live Show', 'event': 'Secret Party!'}, {'title': 'Trial Event: SIFAS Big Live Show', 'event': 'Your Models are Here!'}, {'title': 'Trial Event: SIFAS Big Live Show', 'event': 'Odd Old Town Tour'}, {'title': 'SIFAS Big Live Show Round 1', 'event': 'Refresh with a Hike!'}, {'title': 'SIFAS Big Live Show Round 2', 'event': 'Invitation to a Wonderful Place!'}, {'title': 'SIFAS Big Live Show Round 3', 'event': 'All Aboard the School Idol Train!'}, {'title': 'SIFAS Big Live Show Round 4', 'event': 'Great Battle on the High Seas'}, {'title': 'SIFAS Big Live Show Round 5', 'event': 'Come Enjoy These Special Sweets'}, {'title': 'Mega Live Show!', 'event': 'Music Made Together'}, {'title': 'SIFAS Big Live Show Round 7', 'event': "Cryptid Catchin' Crusade!"}, {'title': 'SIFAS Big Live Show Round 8', 'event': 'Catch the Mischievous Wolf!'}, {'title': 'School Idol Festival Round 1!', 'event': 'Magical Time!'}, {'title': 'SIFAS Big Live Show Round 9', 'event': 'Cooking with Vegetables!'}, {'title': 'SIFAS Big Live Show Round 10', 'event': 'Ice Skating Youth'}, {'title': 'SIFAS Big Live Show Round 11', 'event': 'Hot Spring Rhapsody'}, {'title': 'SIFAS Big Live Show Round 12', 'event': 'Save the Ramen of Joy!'}, {'title': 'SIFAS Big Live Show Round 13', 'event': 'Three Princesses'}, {'title': 'SIFAS Big Live Show Round 14', 'event': 'Singing in the Rain with You'}, {'title': 'SIFAS Big Live Show Round 15', 'event': "Yohane and Hanayo's Whodunit Caper"}, {'title': 'SIFAS Big Live Show Round 16', 'event': "Rina's Creepy Haunted House"}, {'title': '2nd Anniversary SIFAS Big Live Show', 'event': 'Grab Victory in the Sports Battle!'}, {'title': 'SIFAS Big Live Show Round 17', 'event': 'Toy Store Panic'}, {'title': 'SIFAS Big Live Show Round 18', 'event': 'Rebel-ish Makeover'}, {'title': 'SIFAS Big Live Show Round 19', 'event': 'Enjoy the Taste of Fall!'}]
		
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
			
			# strftime('%d %B %Y %H:%M %Z')
			data['event']['start'] = data['event']['start'].strftime('%d %b %Y')
			data['event']['end']   = data['event']['end'].strftime('%d %b %Y')
			
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
	
	def _ordinalize(self, n):
		n = int(n)
		if 11 <= (n % 100) <= 13:
			suffix = 'th'
		else:
			suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
		return str(n) + suffix
	
	def get_banners_with_cards(self):
		banners = self.client.get_banners_with_cards()
		
		banner_title_overrides = dict([
			(21, "Initial SR Shioriko (Nijigasaki Festival)"),
			(48, "Initial SR Mia and Lanzhu"),
		])
		
		now = datetime.now(timezone.utc)
		
		events_per_month = 1
		for banner_id, data in banners.items():
			data['banner']['age'] = now - data['banner']['start']
			
			data['banner']['start'] = data['banner']['start'].strftime('%d %b %Y')
			data['banner']['end']   = data['banner']['end'].strftime('%d %b %Y')
			
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
					data['banner']['title'] = f"{self._ordinalize(data['index'] + 1)} {data['banner']['type'].name} {featured_str}"
		
		return banners
	
	# -------------------------------------------------------------------------------------------
	
	def _get_preload_assets(self):
		preload_assets = []
		preload_asset_files = [
			self.css_settings.output_file,
			os.path.join(CardRotations.OutputDirectory, "js/public.js"),
		]
		preload_asset_files.extend(glob(os.path.join(CardRotations.OutputDirectory, "img/thumbnails/atlas_*_30_*_idolized.png")))
		
		ext_types = {
			'.css' : 'style',
			'.png' : 'image',
			'.js'  : 'script',
		}
		
		for filepath in preload_asset_files:
			rel = 'preload'
			
			# if 'atlas_' in filepath:
			# 	rel = "prefetch"
			
			filepath = filepath.replace('\\', '/')
			basename = os.path.basename(filepath)
			
			filehash = get_file_modifyhash(filepath)
			
			relative_path = filepath.replace('public/', '')
			base, ext = os.path.splitext(relative_path)
			
			preload_assets.append({
				'path'   : f"/{base}.{filehash}{ext}",
				'type'   : ext_types[ext],
				'rel'    : rel,
			})
		
		return preload_assets
		
	def due_for_rendering(self, template_filename):
		if self.args.force or self.args.force_render or self.client.was_database_updated():
			return True
			
		if self.renderer.has_template_changed(template_filename) or self.renderer.is_any_output_missing(template_filename):
			self.renderer.reset_output(template_filename)
			return True
		
		self.renderer.preserve_output(template_filename)
		return False
	
	def generate_pages(self):
		files_to_delete = [x.replace("\\", "/") for x in glob(os.path.join(CardRotations.OutputDirectory, "pages/*.html"))]
		files_to_delete.extend([x.replace("\\", "/") for x in glob(os.path.join(CardRotations.OutputDirectory, "pages/history/*.html"))])
		
		render_start_time = time.perf_counter()
		
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
		
		if self.due_for_rendering("basic_rotation_template.html"):
			# General UR rotations
			ur_rotations = [(group, self.get_general_rotation(group, Rarity.UR)) for group in Group]
			self.renderer.render_and_save("basic_rotation_template.html", "pages/ur_rotations.html", {
				'grouped_rotations'  : ur_rotations,
				'set_label'          : 'Rotation',
				'page_title'         : 'UR Rotations',
				'page_description'   : '''Rotations for all UR cards. <b>Please note:</b> these rotations are automatically laid in the original release
				                          order and manual per-rotation exceptions are not planned for this page beyond adjusting the initial URs.''',
			}, minify=not self.args.dev)
		
			# Festival UR rotations
			festival_rotations = [(group, self.get_source_rotation(group, Source.Festival)) for group in Group]
			self.renderer.render_and_save("basic_rotation_template.html", "pages/festival_rotations.html", {
				'grouped_rotations'  : festival_rotations,
				'set_label'          : 'Rotation',
				'page_title'         : 'Festival UR Rotations',
				'page_description'   : 'Rotations for Festival limited URs scouted exclusively from All Stars Festival banners.',
			}, minify=not self.args.dev)
		
			# Party UR rotations
			party_rotations = [(group, self.get_source_rotation(group, Source.Party)) for group in Group]
			self.renderer.render_and_save("basic_rotation_template.html", "pages/party_rotations.html", {
				'grouped_rotations'  : party_rotations,
				'set_label'          : 'Rotation',
				'page_title'         : 'Party UR Rotations',
				'page_description'   : 'Rotations for Party limited URs scouted exclusively from Party Scouting banners.',
			}, minify=not self.args.dev)
		
			# Event UR rotations
			event_rotations = [(group, self.get_source_rotation(group, Source.Event)) for group in Group]
			self.renderer.render_and_save("basic_rotation_template.html", "pages/event_rotations.html", {
				'grouped_rotations'  : event_rotations,
				'set_label'          : 'Rotation',
				'page_title'         : 'Event UR Rotations',
				'page_description'   : 'Rotations for Event URs awarded in item exchange and story events.',
			}, minify=not self.args.dev)
		
			# SR Sets
			sr_sets = [(group, self.get_sr_sets(group)) for group in Group]
			self.renderer.render_and_save("basic_rotation_template.html", "pages/sr_sets.html", {
				'grouped_rotations'  : sr_sets,
				'set_label'          : 'Set',
				'page_title'         : 'SR Sets',
				'page_description'   : '''SR cards organised into sets by costume or other common theme.''',
			})
		
		# -------------------------------------------------------
		# Event cards info
		
		if self.due_for_rendering("event_cards.html"):
			events_with_cards, zero_feature_members = self.get_events_with_cards()
			self.renderer.render_and_save("event_cards.html", "pages/event_cards.html", {
				'events_with_cards'    : events_with_cards,
				'zero_feature_members' : zero_feature_members,
			})
			
		# -------------------------------------------------------
		# Banner info
		
		if self.due_for_rendering("banners.html"):
			banners_with_cards = self.get_banners_with_cards()
			self.renderer.render_and_save("banners.html", "pages/banners.html", {
				'banners_with_cards' : banners_with_cards,
			})
		
		# -------------------------------------------------------
		# Card history
		
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
						'member_added'   : member_addition_dates[member],
					}, minify=not self.args.dev)
			
		# -------------------------------------------------------
		# Card stats
		
		if self.due_for_rendering("stats.html"):
			general_stats = self.get_general_stats()
			self.renderer.render_and_save("stats.html", "pages/stats.html", {
				'category_tag'   : 'general',
				'general_stats'  : general_stats,
			}, minify=not self.args.dev)
		
			history_category = {
				Source.Unspecified : 'gacha',
				Source.Event       : 'event',
				Source.Gacha       : 'gacha',
				Source.Spotlight   : 'gacha',
				Source.Festival    : 'festival',
				Source.Party       : 'party',
			}
			
			card_stats, category_info, category_has_empty_rows = self.get_card_stats()
			for category_tag in card_stats.keys():
				self.renderer.render_and_save("stats.html", f"pages/stats_{category_tag}.html", {
					'category_tag'   : category_tag,
					'category_data'  : card_stats[category_tag],
					'category_info'  : category_info[category_tag],
					'has_empty_rows' : category_has_empty_rows[category_tag],
					'history_category' : history_category,
				}, minify=not self.args.dev)
		
		# -------------------------------------------------------
		# Index page
		
		if self.due_for_rendering("home.html"):
			self.renderer.render_and_save("home.html", "pages/home.html", {}, minify=not self.args.dev)
		
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
		# Compile and minify CSS
		
		self.processor.compile_css(
			input_files = self.css_settings.input_files,
			output_file = self.css_settings.output_file,
			minify=not self.args.dev,
		)
		
		# -------------------------------------------------------
		# Main index and layout
		
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
