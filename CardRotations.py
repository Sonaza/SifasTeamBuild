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

class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

class CardRotations():
	OutputDirectory = "public"
	
	def __init__(self):
		self.parser = argparse.ArgumentParser(description='Make some card rotations.')
		
		self.parser.add_argument("-f", "--force", help="Force database update regardless of when it was last performed.",
							action="store_true")
		
		self.parser.add_argument("-ra", "--remake-atlas", help="Remake the atlas of thumbnails and the associated CSS code.",
							action="store_true")
		
		self.parser.add_argument("-a", "--auto", help="Flags this update as having been done automatically.",
							action="store_true")
		
		self.parser.add_argument("-dev", help="Flags it as developing build.",
							action="store_true")
		
		self.parser.add_argument("-w", "--watch", help="Instead of building anything start watching for asset changes and rebuild if things are modified.",
							action="store_true")
		
		self.args = self.parser.parse_args()
		
		self.css_settings = dotdict({
			'watch_directory' : "assets/",
			'watched_files'   : [
				"assets/css/*.scss",
			],
			'input_files'     : [
				"public/css/fonts.css",
				"assets/css/atlas.css",
				"assets/css/idols.css",
				"assets/css/style.scss",
				"assets/css/style-mobile.scss",
			],
			'output_file'     : os.path.join(self.OutputDirectory, "css/public.min.css").replace('\\', '/'),
		})
		
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
				Member.Shioriko : [0, 3, 2],
				Member.Lanzhu   : [0, 8],
				Member.Mia      : [0, 8],
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
		
		all_idols = set()
		if group == None:
			for idol in Idols.all_idols:
				all_idols.add(idol.member_id)
		else:
			for idol in Idols.by_group[group]:
				all_idols.add(idol.member_id)
			
		out = []
		for idol in idols:
			out.append((idol.member_id, idol, now - idol.release_date))
			all_idols.remove(idol.member_id)
		
		for member_id in all_idols:
			out.insert(0, (member_id, CardNonExtant(), 0))
			
		return out
	
	def get_card_stats(self):
		categories = {
			'event'     : (Rarity.UR, [Source.Event], ),
			'festival'  : (Rarity.UR, [Source.Festival], ),
			'party'     : (Rarity.UR, [Source.Party], ),
			'spotlight' : (Rarity.UR, [Source.Spotlight, Source.Party], ),
			'limited'   : (Rarity.UR, [Source.Festival, Source.Party], ),
			'gacha'     : (Rarity.UR, [Source.Unspecified, Source.Gacha, Source.Spotlight, Source.Festival, Source.Party], ),
			'ur'        : (Rarity.UR, None, ),
			'sr'        : (Rarity.SR, None, ),
		}
		category_info = {
			'event'      : ( "Event URs",         "Event URs awarded in item exchange and story events." ),
			'festival'   : ( "Festival URs",      "Festival limited URs scouted exclusively from All Stars Festival banners." ),
			'party'      : ( "Party URs",         "Party limited URs scouted exclusively from Party Scouting banners." ),
			'spotlight'  : ( "Party + Spotlight", "Party banners replaced Spotlight banners upon their introduction and release order up until now has followed in its footsteps." ),
			'limited'    : ( "Festival + Party",  "The most recent Festival and Party limited URs. Due to their higher average power level and limited nature, the same member is unlikely to receive two in quick succession." ),
			'gacha'      : ( "Any Gacha UR",      "Any UR scouted from banners using Star Gems." ),
			'ur'         : ( "Any UR",            "Any most recent UR, free or otherwise." ),
			'sr'         : ( "Any SR",            "Any most recent SR, free or otherwise" ),
		}
		
		category_data = defaultdict(dict)
		
		for category, (rarity, sources) in categories.items():
			for group in Group:
				category_data[category][group] = {
					'cards'       : self._time_since_last(idols=self.client.get_newest_idols(group=group, rarity=rarity, source=sources), group=group),
					'show_source' : (not isinstance(sources, list) or len(sources) > 1),
				}
			
			category_data[category]['collapsed'] = {
				'cards'       : self._time_since_last(idols=self.client.get_newest_idols(rarity=rarity, source=sources), group=None),
				'show_source' : (not isinstance(sources, list) or len(sources) > 1),
			}
		
		return (category_data, category_info)
	
	# -------------------------------------------------------------------------------------------
	
	def get_events_with_cards(self):
		events = self.client.get_events_with_cards()
		features = self.client.get_event_features_per_member()
		
		zero_feature_members = [member for member, num_features in features.items() if num_features == 0]
		
		# sbl_events = [{'title': 'Trial Event: SIFAS Big Live Show', 'event': 'Secret Party!'}, {'title': 'Trial Event: SIFAS Big Live Show', 'event': 'Your Models are Here!'}, {'title': 'Trial Event: SIFAS Big Live Show', 'event': 'Odd Old Town Tour'}, {'title': 'SIFAS Big Live Show Round 1', 'event': 'Refresh with a Hike!'}, {'title': 'SIFAS Big Live Show Round 2', 'event': 'Invitation to a Wonderful Place!'}, {'title': 'SIFAS Big Live Show Round 3', 'event': 'All Aboard the School Idol Train!'}, {'title': 'SIFAS Big Live Show Round 4', 'event': 'Great Battle on the High Seas'}, {'title': 'SIFAS Big Live Show Round 5', 'event': 'Come Enjoy These Special Sweets'}, {'title': 'Mega Live Show!', 'event': 'Music Made Together'}, {'title': 'SIFAS Big Live Show Round 7', 'event': "Cryptid Catchin' Crusade!"}, {'title': 'SIFAS Big Live Show Round 8', 'event': 'Catch the Mischievous Wolf!'}, {'title': 'School Idol Festival Round 1!', 'event': 'Magical Time!'}, {'title': 'SIFAS Big Live Show Round 9', 'event': 'Cooking with Vegetables!'}, {'title': 'SIFAS Big Live Show Round 10', 'event': 'Ice Skating Youth'}, {'title': 'SIFAS Big Live Show Round 11', 'event': 'Hot Spring Rhapsody'}, {'title': 'SIFAS Big Live Show Round 12', 'event': 'Save the Ramen of Joy!'}, {'title': 'SIFAS Big Live Show Round 13', 'event': 'Three Princesses'}, {'title': 'SIFAS Big Live Show Round 14', 'event': 'Singing in the Rain with You'}, {'title': 'SIFAS Big Live Show Round 15', 'event': "Yohane and Hanayo's Whodunit Caper"}, {'title': 'SIFAS Big Live Show Round 16', 'event': "Rina's Creepy Haunted House"}, {'title': '2nd Anniversary SIFAS Big Live Show', 'event': 'Grab Victory in the Sports Battle!'}, {'title': 'SIFAS Big Live Show Round 17', 'event': 'Toy Store Panic'}, {'title': 'SIFAS Big Live Show Round 18', 'event': 'Rebel-ish Makeover'}, {'title': 'SIFAS Big Live Show Round 19', 'event': 'Enjoy the Taste of Fall!'}]
		
		sbl_reference_point = {
			'event_id' : 24,
			'date'     : datetime(2022, 1, 1),
		}
		today = datetime.today()
		while sbl_reference_point['date'].month != today.month:
			if (sbl_reference_point['event_id'] + 1) not in events:
				break

			sbl_reference_point['event_id'] += 1
			sbl_reference_point['date'] += relativedelta(months=1)
		
		for event_id, data in events.items():
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
			
			diff = event_id - sbl_reference_point['event_id']
			estimated_addition = sbl_reference_point['date'] + relativedelta(months=diff)
			data['sbl'] = estimated_addition.strftime('%b %Y')
		
		return events, zero_feature_members
	
	# -------------------------------------------------------------------------------------------
	
	def _get_preload_assets(self):
		preload_assets = []
		preload_asset_files = [
			self.css_settings.output_file,
			os.path.join(CardRotations.OutputDirectory, "js/public.js"),
		]
		preload_asset_files.extend(glob(os.path.join(CardRotations.OutputDirectory, "img/thumbnails/atlas_*_30_*.png")))
		
		ext_types = {
			'.css' : 'style',
			'.png' : 'image',
			'.js'  : 'script',
		}
		
		for filepath in preload_asset_files:
			filepath = filepath.replace('\\', '/')
			basename = os.path.basename(filepath)
			
			filehash = get_file_modifyhash(filepath)
			
			relative_path = filepath.replace('public/', '')
			base, ext = os.path.splitext(relative_path)
			
			preload_assets.append({
				'path'   : f"/{base}.{filehash}{ext}",
				'type'   : ext_types[ext],
			})
		
		return preload_assets
	
	def generate_pages(self):
		files_to_delete = [x.replace("\\", "/") for x in glob(os.path.join(CardRotations.OutputDirectory, "pages/*.html"))]
		
		# -------------------------------------------------------
		# Per school UR attribute-type arrays
		
		idol_arrays = [(group, *self.get_attribute_type_array(group)) for group in Group]
		for data in idol_arrays:
			output_file = self.renderer.render_and_save("attribute_type_array.html", f"pages/idol_arrays_{data[0].tag}.html", {
				'idol_arrays'        : [ data ],
			}, minify=not self.args.dev)
		
		# -------------------------------------------------------
		# General UR rotations
		
		ur_rotations = [(group, self.get_general_rotation(group, Rarity.UR)) for group in Group]
		self.renderer.render_and_save("basic_rotation_template.html", "pages/ur_rotations.html", {
			'grouped_rotations'  : ur_rotations,
			'set_label'          : 'Rotation',
			'page_title'         : 'UR Rotations',
			'page_description'   : 'Rotations for all UR cards.',
		}, minify=not self.args.dev)
		
		# -------------------------------------------------------
		# Festival UR rotations
		
		festival_rotations = [(group, self.get_source_rotation(group, Source.Festival)) for group in Group]
		self.renderer.render_and_save("basic_rotation_template.html", "pages/festival_rotations.html", {
			'grouped_rotations'  : festival_rotations,
			'set_label'          : 'Rotation',
			'page_title'         : 'Festival UR Rotations',
			'page_description'   : 'Rotations for Festival limited URs scouted exclusively from All Stars Festival banners.',
		}, minify=not self.args.dev)
		
		# -------------------------------------------------------
		# Party UR rotations
		
		party_rotations = [(group, self.get_source_rotation(group, Source.Party)) for group in Group]
		self.renderer.render_and_save("basic_rotation_template.html", "pages/party_rotations.html", {
			'grouped_rotations'  : party_rotations,
			'set_label'          : 'Rotation',
			'page_title'         : 'Party UR Rotations',
			'page_description'   : 'Rotations for Party limited URs scouted exclusively from Party Scouting banners.',
		}, minify=not self.args.dev)
		
		# -------------------------------------------------------
		# Event UR rotations
		
		event_rotations = [(group, self.get_source_rotation(group, Source.Event)) for group in Group]
		self.renderer.render_and_save("basic_rotation_template.html", "pages/event_rotations.html", {
			'grouped_rotations'  : event_rotations,
			'set_label'          : 'Rotation',
			'page_title'         : 'Event UR Rotations',
			'page_description'   : 'Rotations for Event URs awarded in item exchange and story events.',
		}, minify=not self.args.dev)
		
		# -------------------------------------------------------
		# Event cards info
		
		events_with_cards, zero_feature_members = self.get_events_with_cards()
		self.renderer.render_and_save("event_cards.html", "pages/event_cards.html", {
			'events_with_cards'    : events_with_cards,
			'zero_feature_members' : zero_feature_members,
		})
		
		# -------------------------------------------------------
		# SR Sets
		
		sr_sets = [(group, self.get_general_rotation(group, Rarity.SR)) for group in Group]
		self.renderer.render_and_save("basic_rotation_template.html", "pages/sr_sets.html", {
			'grouped_rotations'  : sr_sets,
			'set_label'          : 'Set',
			'page_title'         : 'SR Sets',
			'page_description'   : 'Rotations for SR sets. SR release order seems highly variable (mainly the new girls not fitting in neat cycles) so this page may or may not break.',
		})
		
		# -------------------------------------------------------
		# Card stats
		
		general_stats = self.get_general_stats()
		self.renderer.render_and_save("stats.html", "pages/stats.html", {
			'category_tag'   : 'general',
			'general_stats'  : general_stats,
		}, minify=not self.args.dev)
		
		card_stats, category_info = self.get_card_stats()
		for category_tag in card_stats.keys():
			self.renderer.render_and_save("stats.html", f"pages/stats_{category_tag}.html", {
				'category_tag'   : category_tag,
				'category_data'  : card_stats[category_tag],
				'category_info'  : category_info[category_tag],
			}, minify=not self.args.dev)
		
		# -------------------------------------------------------
		# Index page
		
		self.renderer.render_and_save("home.html", "pages/home.html", {}, minify=not self.args.dev)
		
		# -------------------------------------------------------
		# Compile and minify CSS
		
		self.processor.compile_css(
			input_files = self.css_settings.input_files,
			output_file = self.css_settings.output_file,
			minify=True,
		)
		
		# -------------------------------------------------------
		# Main index and layout
		
		preload_assets = self._get_preload_assets()
		
		now = datetime.now(timezone.utc)
		self.renderer.render_and_save("main_layout.php", "views/content_index.php", {
			'last_update'           : now.strftime('%d %B %Y %H:%M %Z'),
			'last_update_timestamp' : now.isoformat(),
			'preloads' : preload_assets
		}, minify=False, output_basepath='')
		
		# -------------------------------------------------------
		# Error Pages
		
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
		
		self.renderer.render_and_save("crawler.html", "crawler.html", {}, minify=True)
		
		# -------------------------------------------------------
		# .htaccess
		
		self.renderer.render_and_save("template.htaccess", ".htaccess", {
			'preloads' : preload_assets
		}, minify=False, generated_note=True)
		
		# -------------------------------------------------------
		# File cleanup
		
		for file in files_to_delete:
			if file in self.renderer.rendered_pages: continue
			
			print(f"Removing outdated file  {file}")
			os.remove(file)
		
		print("\nAll done!\n")

# -------------------------------------------------------------------------------------------

if __name__ == "__main__":
	cr = CardRotations()
	
	buildstatus = {
		"timestamp" : datetime.now(timezone.utc).isoformat(),
		"handled"   : None,
		"auto"      : cr.args.auto,
		"forced"    : cr.args.force,
		"success"   : None,
		"message"   : "",
	}
	build_exception = None
	
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
