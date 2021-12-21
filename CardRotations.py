from operator import itemgetter
from enum import Enum
from collections import defaultdict, namedtuple

from IdolDatabase import *
from IdolKiraraClient import KiraraClient, KiraraIdol

import os
import time
from datetime import datetime, timezone
from jinja2 import Environment, PackageLoader, FileSystemLoader, select_autoescape

GroupInfo = namedtuple("GroupInfo", "tag name")

class CardNonExtant(): pass
class CardMissing(): pass

def is_valid_card(value):
	return isinstance(value, KiraraIdol)

def is_missing_card(value):
	return isinstance(value, CardMissing)
	
def is_nonextant_card(value):
	return isinstance(value, CardNonExtant)

def ordinalize(number):
	suffix = "th"
	if (number % 10) == 1 and number != 11:
		suffix = "st"
	elif (number % 10) == 2 and number != 12:
		suffix = "nd"
	elif (number % 10) == 3 and number != 13:
		suffix = "rd"
		
	return f"{number}{suffix}"
	
# def include_page(filepath):
# 	filepath = os.path.join("output", filepath)
# 	if not os.path.exists(filepath): return f"<h1>Error: {filepath} does not exist.</h1>"
# 	with open(filepath, encoding="utf8") as f:
# 		return f.read()
# 	return f"<h1>Error: Failed to open {filepath}.</h1>"

class CardThumbnails():
	def __init__(self, client):
		self.client = client
	
	def _download_file(self, url, target_path):
		import requests
		r = requests.get(url)
		if r.status_code == 200:
			with open(target_path, "wb") as f:
				f.write(r.content)
				f.close()
			return True
			
		print(f"Return code {r.status_code}, failed to download resource: {url}")
		return False
				
	def download_thumbnails(self):
		has_new_thumbnails = False
		
		cards = self.client.get_all_idols()
		for card in cards:
			normal_path = f"thumbnails/single/{card.member_id.value}_{card.ordinal}_normal.png"
			if not os.path.exists(normal_path):
				print(normal_path, end='')
				if self._download_file(card.data["normal_appearance"]["thumbnail_asset_path"], normal_path):
					print(" OK")
					has_new_thumbnails = True
				else:
					print(" FAIL!")
			
			idolized_path = f"thumbnails/single/{card.member_id.value}_{card.ordinal}_idolized.png"
			if not os.path.exists(idolized_path):
				print(idolized_path, end='')
				if self._download_file(card.data["idolized_appearance"]["thumbnail_asset_path"], idolized_path):
					print(" OK")
					has_new_thumbnails = True
				else:
					print(" FAIL!")
		
		return has_new_thumbnails
	
	def make_atlas(self):
		from PIL import Image
		
		atlas_by_ordinal = {}
		sizes = [80]
		rarities = [Rarity.SR, Rarity.UR]
		
		for rarity in rarities:
			for group in Group:
				cards = self.client.get_idols_by_group(group, rarity)
				cards_per_girl = defaultdict(list)
				for card in cards:
					cards_per_girl[card.member_id].append(card)
				
				num_rotations = 0
				num_members = len(Idols.by_group[group])
				for member_id, cards in cards_per_girl.items():
					num_rotations = max(num_rotations, len(cards))
				
				for size in sizes:
					thumbnail_size = (size, size)
					image_size = (thumbnail_size[0] * num_members, thumbnail_size[1] * (num_rotations + 1))
					atlas_normal = Image.new('RGB', image_size, (0, 0, 0,))
					atlas_idolized = Image.new('RGB', image_size, (0, 0, 0,))
					
					missing_icon = Image.open("thumbnails/missing_icon.png")
					missing_icon.thumbnail(thumbnail_size)
					atlas_normal.paste(missing_icon, (0, 0))
					atlas_idolized.paste(missing_icon, (0, 0))
					
					for column_index, ordered_member_id in enumerate(Idols.member_order[group]):
						for row_index, card in enumerate(cards_per_girl[ordered_member_id]):
							target_coordinates = (thumbnail_size[0] * column_index, thumbnail_size[1] * (row_index + 1))
							
							atlas_by_ordinal[card.ordinal] = (group, rarity, 0, target_coordinates)
							
							normal = f"thumbnails/single/{card.member_id.value}_{card.ordinal}_normal.png"
							im_normal = Image.open(normal)
							im_normal.thumbnail(thumbnail_size)
							atlas_normal.paste(im_normal, target_coordinates)
							
							idolized = f"thumbnails/single/{card.member_id.value}_{card.ordinal}_idolized.png"
							im_idolized = Image.open(idolized)
							im_idolized.thumbnail(thumbnail_size)
							atlas_idolized.paste(im_idolized, target_coordinates)
							
							im_normal.close()
							im_idolized.close()
						
					atlas_normal.save(f'output/img/thumbnails/atlas_{group.value}_{rarity.value}_0_normal.png', 'PNG')
					atlas_idolized.save(f'output/img/thumbnails/atlas_{group.value}_{rarity.value}_0_idolized.png', 'PNG')
				
		groups = []
		for rarity in rarities:
			for group in Group:
				groups.append(f"                         .card-thumbnail.group-{group.value}-{rarity.value} {{ background: url('/img/thumbnails/atlas_{group.value}_{rarity.value}_0_normal.png') no-repeat; }}")
				groups.append(f".use-idolized-thumbnails .card-thumbnail.group-{group.value}-{rarity.value} {{ background: url('/img/thumbnails/atlas_{group.value}_{rarity.value}_0_idolized.png') no-repeat; }}")
				
		with open("output/css/atlas.css", "w", encoding="utf8") as f:
			for line in groups:
				f.write(line + "\n")
			
			for ordinal, (group, rarity, atlas_index, coordinates) in atlas_by_ordinal.items():
				line = f".card-thumbnail.card-{ordinal} {{ background-position: {-coordinates[0]}px {-coordinates[1]}px !important; }}"
				f.write(line + "\n")
			
			f.close()
		

class CardRotations():
	
	def __init__(self):
		self.client = KiraraClient()
		self.jinja = Environment(
		    # loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__)), encoding='utf-8'),
		    loader=PackageLoader("CardRotations", encoding='utf-8'),
		    # autoescape=select_autoescape()
		)
		
		self.thumbnails = CardThumbnails(self.client)
		if self.thumbnails.download_thumbnails():
			self.thumbnails.make_atlas()
		
	def _sort_rotation(self, group, rotation, order):
		output = []
		for ordered_member_id in order:
			if ordered_member_id in rotation:
				output.append((ordered_member_id, rotation[ordered_member_id]))
		
		return output
	
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
			
			rotations.append(self._sort_rotation(group, current_rotation, Idols.member_order[group]))
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
			
			# if idol.member_id in member_delays[source]:
			# 	cards_per_girl[idol.member_id].extend([CardNonExtant()] * member_delays[source][idol.member_id])

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
			
			rotations.append(self._sort_rotation(group, current_rotation, Idols.member_order[group]))
			rotation_index += 1
		
		return rotations
		
	def _render_and_save(self, template_path, output_path, data):
		print(f"Rendering {template_path} to {output_path}... ", end='')
		
		# template = self.jinja.get_template(os.path.join("templates", template_path).replace("\\","/"))
		template = self.jinja.get_template(template_path)
		rendered_output = template.render(data)
		
		with open(os.path.join("output", output_path), "w", encoding="utf8") as f:
			f.write(rendered_output)
			f.close()
		
		print("Done")
		
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
	
	def _time_since_last(self, group, idols):
		now = datetime.now(timezone.utc)
		
		all_idols = set()
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
					'cards'       : self._time_since_last(group, self.client.get_newest_idols(group=group, rarity=rarity, source=sources)),
					'show_source' : (not isinstance(sources, list) or len(sources) > 1),
				}
		
		return result
	
	def generate_pages(self):
		group_info = {
			Group.Muse       : GroupInfo(tag="muse",       name="µ's"),
			Group.Aqours     : GroupInfo(tag="aqours",     name="Aqours"),
			Group.Nijigasaki : GroupInfo(tag="nijigasaki", name="Nijigasaki"),
		}
		
		self.jinja.globals.update({
			'Idols'     : Idols,
			'Attribute' : [Attribute.Smile, Attribute.Pure, Attribute.Cool, Attribute.Active, Attribute.Natural, Attribute.Elegant, ],
			'Type'      : [Type.Vo, Type.Sp, Type.Gd, Type.Sk, ],
			'GroupInfo' : group_info,
			
			'is_valid_card':     is_valid_card,
			'is_missing_card':   is_missing_card,
			'is_nonextant_card': is_nonextant_card,
			
			'ordinalize' : ordinalize,
			
		})
		
		idol_arrays = [
			( Group.Muse,       *self.get_attribute_type_array(Group.Muse) ),
			( Group.Aqours,     *self.get_attribute_type_array(Group.Aqours) ),
			( Group.Nijigasaki, *self.get_attribute_type_array(Group.Nijigasaki) ),
		]
		for data in idol_arrays:
			self._render_and_save("attribute_type_array.html", f"pages/idol_arrays_{group_info[data[0]].tag}.html", {
				'idol_arrays'        : [ data ],
			})
		
		ur_rotations = [
			( Group.Muse,       self.get_general_rotation(Group.Muse,       Rarity.UR)),
			( Group.Aqours,     self.get_general_rotation(Group.Aqours,     Rarity.UR)),
			( Group.Nijigasaki, self.get_general_rotation(Group.Nijigasaki, Rarity.UR)),
		]
		self._render_and_save("basic_rotation_template.html", "pages/ur_rotations.html", {
			'grouped_rotations'  : ur_rotations,
			'set_label'          : 'Rotation',
			'page_title'         : 'UR Rotations',
			'page_description'   : 'Rotations for any UR cards released.',
		})
		
		festival_rotations = [
			( Group.Muse,       self.get_source_rotation(Group.Muse,       Source.Festival)),
			( Group.Aqours,     self.get_source_rotation(Group.Aqours,     Source.Festival)),
			( Group.Nijigasaki, self.get_source_rotation(Group.Nijigasaki, Source.Festival)),
		]
		self._render_and_save("basic_rotation_template.html", "pages/festival_rotations.html", {
			'grouped_rotations'  : festival_rotations,
			'set_label'          : 'Rotation',
			'page_title'         : 'Festival UR Rotations',
			'page_description'   : 'Rotations for Festival limited URs scouted exclusively from All Stars Festival banners.',
		})
		
		party_rotations = [
			( Group.Muse,       self.get_source_rotation(Group.Muse,       Source.Party)),
			( Group.Aqours,     self.get_source_rotation(Group.Aqours,     Source.Party)),
			( Group.Nijigasaki, self.get_source_rotation(Group.Nijigasaki, Source.Party)),
		]
		self._render_and_save("basic_rotation_template.html", "pages/party_rotations.html", {
			'grouped_rotations'  : party_rotations,
			'set_label'          : 'Rotation',
			'page_title'         : 'Party UR Rotations',
			'page_description'   : 'Rotations for Party limited URs scouted exclusively from Party Scouting banners.',
		})
		
		event_rotations = [
			( Group.Muse,       self.get_source_rotation(Group.Muse,       Source.Event)),
			( Group.Aqours,     self.get_source_rotation(Group.Aqours,     Source.Event)),
			( Group.Nijigasaki, self.get_source_rotation(Group.Nijigasaki, Source.Event)),
		]
		self._render_and_save("basic_rotation_template.html", "pages/event_rotations.html", {
			'grouped_rotations'  : event_rotations,
			'set_label'          : 'Rotation',
			'page_title'         : 'Event UR Rotations',
			'page_description'   : 'Rotations for Event URs awarded in item exchange and story events.',
		})
		
		sr_sets = [
			( Group.Muse,       self.get_general_rotation(Group.Muse,       Rarity.SR)),
			( Group.Aqours,     self.get_general_rotation(Group.Aqours,     Rarity.SR)),
			( Group.Nijigasaki, self.get_general_rotation(Group.Nijigasaki, Rarity.SR)),
		]
		self._render_and_save("basic_rotation_template.html", "pages/sr_sets.html", {
			'grouped_rotations'  : sr_sets,
			'set_label'          : 'Set',
			'page_title'         : 'SR Sets',
			'page_description'   : 'Rotations for SR sets. SR release order seems highly variable (and they do not fit into neat rotations) so this page the most likely to have errors.',
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
				'gacha'      : ( "Any Gacha UR",      "Any UR scouted from gacha banners using Star Gems." ),
				'ur'         : ( "Any UR",            "Any most recent UR, free or otherwise." ),
				'sr'         : ( "Any SR",            "Any most recent SR, free or otherwise" ),
			}
		})
		
		self._render_and_save("main.html", "pages/main.html", {
			
		})
		
		# self._render_and_save("combined_layout.html", "index.html", {})
		

##################################

if __name__ == "__main__":
	cr = CardRotations()
	cr.generate_pages()

	print()
