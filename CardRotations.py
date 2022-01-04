from IdolDatabase import *
from CardThumbnails import CardThumbnails

import argparse
import os
import time
from glob import glob
from operator import itemgetter
from collections import defaultdict, namedtuple
from datetime import datetime, timezone

from jinja2 import Environment, PackageLoader, FileSystemLoader, select_autoescape
import htmlmin, cssmin

class CardNonExtant(): pass
class CardMissing(): pass

class CardRotations():
	OutputDirectory = "output"
	
	@staticmethod
	def is_valid_card(value):     return isinstance(value, KiraraIdol)
	@staticmethod
	def is_missing_card(value):   return isinstance(value, CardMissing)
	@staticmethod
	def is_nonextant_card(value): return isinstance(value, CardNonExtant)

	@staticmethod
	def ordinalize(n):
		n = int(n)
		if 11 <= (n % 100) <= 13:
			suffix = 'th'
		else:
			suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
		return str(n) + suffix
		
	@staticmethod
	def pluralize(value, singular, plural):
		if abs(value) == 1:
			return f"{abs(value)} {singular}"
		else:
			return f"{abs(value)} {plural}"

	@staticmethod
	def format_days(value):
		if value > 0:
			return f"{CardRotations.pluralize(value, 'day', 'days')} ago"
		elif value == 0:
			return "Today"
		else:
			return f"In {CardRotations.pluralize(value, 'day', 'days')}"
		
	@staticmethod
	def conditional_css(class_names, condition):
		assert isinstance(class_names, str) or isinstance(class_names, list) or isinstance(class_names, tuple)
		assert isinstance(condition, bool)
		
		if isinstance(class_names, str): class_names = [class_names, '']
		elif len(class_names) == 1:      class_names = [class_names[0], '']
			
		if condition:
			return class_names[0]
		else:
			return class_names[1]
			
	@staticmethod
	def cache_buster(filename):
		full_path = os.path.normpath(CardRotations.OutputDirectory + '/' + filename)
		if not os.path.exists(full_path):
			print(f"Cache busting path {full_path} does not exist!")
			return filename
			
		modify_time = os.stat(full_path).st_mtime
		name, ext = os.path.splitext(filename)
		hashvalue = hash(modify_time) % 16711425
		return f"{name}.{hashvalue:06x}{ext}"
		
	@staticmethod
	def include_page(filepath):
		# filepath = os.path.join("output", filepath)
		if not os.path.exists(filepath): return f"<h1>Error: {filepath} does not exist.</h1>"
		with open(filepath, encoding="utf8") as f:
			return f.read()
		return f"<h1>Error: Failed to open {filepath}.</h1>"
	
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
		
		self.args = self.parser.parse_args()
		
		if self.args.dev:
			print("------ BUILDING IN DEV MODE ------")
		else:
			print("------ BUILDING IN PROD MODE ------")
		print()
		
		try:
			print("Current user id", os.getuid())
		except:
			pass
		print("Current Working Directory", os.getcwd())
		
		self.client = KiraraClient()
		self.client.cache_all_idols(forced=self.args.force)
		
		self.jinja = Environment(
			# loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__)), encoding='utf-8'),
			loader=PackageLoader("CardRotations", encoding='utf-8'),
			# autoescape=select_autoescape()
		)
		
		self.jinja.filters.update({
			'format_days'     : CardRotations.format_days,
			'pluralize'       : CardRotations.pluralize,
			'ordinalize'      : CardRotations.ordinalize,
			
			'conditional_css' : CardRotations.conditional_css,
		})
		
		self.jinja.globals.update({
			# Python built in functions
			'reversed'    : reversed,
			
			# Application related variables
			'cmd_args'      : self.args,
			
			# Application related global enums
			'Attribute' : Attribute.get_valid(),
			'Type'      : Type.get_valid(),
			
			# Page specific functions
			'is_valid_card'     : CardRotations.is_valid_card,
			'is_missing_card'   : CardRotations.is_missing_card,
			'is_nonextant_card' : CardRotations.is_nonextant_card,
			
			'include_page' : CardRotations.include_page,
			
			# Systems stuff
			'cache_buster'      : CardRotations.cache_buster,
		})
		
		self.thumbnails = CardThumbnails(self.client, CardRotations.OutputDirectory)
		if self.thumbnails.download_thumbnails() or self.args.remake_atlas:
			self.thumbnails.make_atlas()
		
	def _sort_rotation(self, group, rotation, order):
		output = []
		for ordered_member_id in order:
			if ordered_member_id in rotation:
				output.append((ordered_member_id, rotation[ordered_member_id]))
		
		return output
		
	def _render_and_save(self, template_filename, output_filename, data, minify=True):
		print(f"Rendering {template_filename} to {output_filename}... ", end='')
		
		# template = self.jinja.get_template(os.path.join("templates", template_filename).replace("\\","/"))
		template = self.jinja.get_template(template_filename)
		rendered_output = template.render(data)
		
		if minify:
			rendered_output = htmlmin.minify(rendered_output, remove_empty_space=True)
		
		with open(os.path.join(CardRotations.OutputDirectory, output_filename), "w", encoding="utf8") as f:
			f.write(rendered_output)
			f.close()
		
		print("Done")
	
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
		
		order = Idols.member_order[group]
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
					(0, "1st Nijigasaki Solo"),
					(5, "3rd Nijigasaki Solo"),
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
						
						if set_title == None and rarity == Rarity.SR and CardRotations.is_valid_card(cards[rotation_index]):
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
		
			rotations.append(( self._sort_rotation(group, current_rotation, Idols.member_order[group]), set_title ))
			rotation_index += 1
		
		return rotations
	
	def get_source_rotation(self, group : Group, source : Source):
		member_delays = {
			Source.Event : {
				Member.Shioriko : 1,
				Member.Lanzhu   : 1,
				Member.Mia      : 1,
			},
			Source.Festival : {
				Member.Shioriko : 0,
				Member.Lanzhu   : 0,
				Member.Mia      : 0,
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
			
			rotations.append(( self._sort_rotation(group, current_rotation, Idols.member_order[group]), None ))
			rotation_index += 1
		
		return rotations
		
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
		
		return self._sort_rotation(group, stats, Idols.member_order[group])
	
	def get_general_stats(self):
		stats = {}
		for group in Group:
			stats[group] = self._make_general_stats(group=group)
			
		return stats
	
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
		
		result = defaultdict(dict)
		for category, (rarity, sources) in categories.items():
			for group in Group:
				result[category][group] = {
					'cards'       : self._time_since_last(idols=self.client.get_newest_idols(group=group, rarity=rarity, source=sources), group=group),
					'show_source' : (not isinstance(sources, list) or len(sources) > 1),
				}
			
			result[category]['collapsed'] = {
				'cards'       : self._time_since_last(idols=self.client.get_newest_idols(rarity=rarity, source=sources), group=None),
				'show_source' : (not isinstance(sources, list) or len(sources) > 1),
			}
		
		return result
	
	def generate_pages(self):
		for file in glob(os.path.join(CardRotations.OutputDirectory, "pages/*.html")):
			print("Removing", file)
			os.remove(file)
		
		idol_arrays = [(group, *self.get_attribute_type_array(group)) for group in Group]
		for data in idol_arrays:
			self._render_and_save("attribute_type_array.html", f"pages/idol_arrays_{data[0].tag}.html", {
				'idol_arrays'        : [ data ],
			}, minify=not self.args.dev)
		
		ur_rotations = [(group, self.get_general_rotation(group, Rarity.UR)) for group in Group]
		self._render_and_save("basic_rotation_template.html", "pages/ur_rotations.html", {
			'grouped_rotations'  : ur_rotations,
			'set_label'          : 'Rotation',
			'page_title'         : 'UR Rotations',
			'page_description'   : 'Rotations for all UR cards.',
		}, minify=not self.args.dev)
		
		festival_rotations = [(group, self.get_source_rotation(group, Source.Festival)) for group in Group]
		self._render_and_save("basic_rotation_template.html", "pages/festival_rotations.html", {
			'grouped_rotations'  : festival_rotations,
			'set_label'          : 'Rotation',
			'page_title'         : 'Festival UR Rotations',
			'page_description'   : 'Rotations for Festival limited URs scouted exclusively from All Stars Festival banners.',
		}, minify=not self.args.dev)
		
		party_rotations = [(group, self.get_source_rotation(group, Source.Party)) for group in Group]
		self._render_and_save("basic_rotation_template.html", "pages/party_rotations.html", {
			'grouped_rotations'  : party_rotations,
			'set_label'          : 'Rotation',
			'page_title'         : 'Party UR Rotations',
			'page_description'   : 'Rotations for Party limited URs scouted exclusively from Party Scouting banners.',
		}, minify=not self.args.dev)
		
		event_rotations = [(group, self.get_source_rotation(group, Source.Event)) for group in Group]
		self._render_and_save("basic_rotation_template.html", "pages/event_rotations.html", {
			'grouped_rotations'  : event_rotations,
			'set_label'          : 'Rotation',
			'page_title'         : 'Event UR Rotations',
			'page_description'   : 'Rotations for Event URs awarded in item exchange and story events.',
		}, minify=not self.args.dev)
		
		sr_sets = [(group, self.get_general_rotation(group, Rarity.SR)) for group in Group]
		self._render_and_save("basic_rotation_template.html", "pages/sr_sets.html", {
			'grouped_rotations'  : sr_sets,
			'set_label'          : 'Set',
			'page_title'         : 'SR Sets',
			'page_description'   : 'Rotations for SR sets. SR release order seems highly variable (mainly the new girls not fitting in neat cycles) so this page may or may not break.',
		})
		
		general_stats = self.get_general_stats()
		card_stats = self.get_card_stats()
		self._render_and_save("stats.html", "pages/stats.html", {
			'general_stats'  : general_stats,
			'card_stats'     : card_stats,
			'categories'     : {
				'event'      : ( "Event URs",         "Event URs awarded in item exchange and story events." ),
				'festival'   : ( "Festival URs",      "Festival limited URs scouted exclusively from All Stars Festival banners." ),
				'party'      : ( "Party URs",         "Party limited URs scouted exclusively from Party Scouting banners." ),
				'spotlight'  : ( "Party + Spotlight", "Party banners replaced Spotlight banners upon their introduction and release order up until now has followed in its footsteps." ),
				'limited'    : ( "Festival + Party",  "The most recent Festival and Party limited URs. Due to their higher average power level and limited nature, the same member is unlikely to receive two in quick succession." ),
				'gacha'      : ( "Any Gacha UR",      "Any UR scouted from banners using Star Gems." ),
				'ur'         : ( "Any UR",            "Any most recent UR, free or otherwise." ),
				'sr'         : ( "Any SR",            "Any most recent SR, free or otherwise" ),
			}
		}, minify=not self.args.dev)
		
		self._render_and_save("home.html", "pages/home.html", {}, minify=not self.args.dev)
		
		# self._minify_css(
		# 	[
		# 		"fonts.css",
		# 		"atlas.css",
		# 		"idols.css",
		# 		"style.css",
		# 	],
		# 	"public.css"
		# )
		
		now = datetime.now(timezone.utc)
		self._render_and_save("main_layout.html", "index.html", {
			'last_update'           : now.strftime('%d %B %Y %H:%M %Z'),
			'last_update_timestamp' : now.isoformat(),
		}, minify=False)
		
		print("\nAll done!\n")
	
	def _minify_css(self, source, destination):
		code = ""
		
		for file in source:
			path = os.path.join(CardRotations.OutputDirectory, "css", file)
			code += open(path, "r", encoding="utf8").read() + "\n"
		
		minified = cssmin.cssmin(code)
		
		print(f"CSS Minify reduced size from {len(code) / 1024:.2f} KB to {len(minified) / 1024:.2f} KB. Yay!")
		
		output_path = os.path.join(CardRotations.OutputDirectory, "css", destination)
		with open(output_path, "w", encoding="utf8") as f:
			f.write(minified)
			f.close()
		

##################################

if __name__ == "__main__":
	cr = CardRotations()
	
	try:
		cr.generate_pages()
	except Exception as e:
		print(e)
		raise e

	print()
