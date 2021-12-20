from operator import itemgetter
from enum import Enum
from collections import defaultdict

from IdolDatabase import *
from IdolKiraraClient import KiraraClient, KiraraIdol

import os
import time
from datetime import datetime, timezone
from jinja2 import Environment, PackageLoader, FileSystemLoader, select_autoescape

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
			print(f"{Idols.by_member_id[member_id].first_name:>10} has {len(cards):>2} URs")
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
			print(f"{Idols.by_member_id[member_id].first_name:>10} has {len(cards):>2} URs")
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
			out.append((member_id, CardNonExtant(), 0))
			
		return out
	
	def get_card_stats(self):
		result = {
			'event' : {
				Group.Muse       : self._time_since_last(Group.Muse, self.client.get_newest_idols(group=Group.Muse,       rarity=Rarity.UR, source=Source.Event)),
				Group.Aqours     : self._time_since_last(Group.Aqours, self.client.get_newest_idols(group=Group.Aqours,     rarity=Rarity.UR, source=Source.Event)),
				Group.Nijigasaki : self._time_since_last(Group.Nijigasaki, self.client.get_newest_idols(group=Group.Nijigasaki, rarity=Rarity.UR, source=Source.Event)),
			},
		}
		
		return result
	
	def generate_pages(self):
		def include_page(filepath):
			filepath = os.path.join("output", filepath)
			if not os.path.exists(filepath): return f"<h1>Error: {filepath} does not exist.</h1>"
			with open(filepath, encoding="utf8") as f:
				return f.read()
			return f"<h1>Error: Failed to open {filepath}.</h1>"
		
		self.jinja.globals.update({
			'Idols'     : Idols,
			'Attribute' : [Attribute.Smile, Attribute.Pure, Attribute.Cool, Attribute.Active, Attribute.Natural, Attribute.Elegant, ],
			'Type'      : [Type.Vo, Type.Sp, Type.Gd, Type.Sk, ],
			
			'is_valid_card':     is_valid_card,
			'is_missing_card':   is_missing_card,
			'is_nonextant_card': is_nonextant_card,
			
			'ordinalize'    : ordinalize,
			'include'       : include_page,
		})
		
		idol_arrays = [
			( "muse",       "µ's",        *self.get_attribute_type_array(Group.Muse) ),
			( "aqours",     "Aqours",     *self.get_attribute_type_array(Group.Aqours) ),
			( "nijigasaki", "Nijigasaki", *self.get_attribute_type_array(Group.Nijigasaki) ),
		]
		for data in idol_arrays:
			self._render_and_save("attribute_type_array.html", f"pages/idol_arrays_{data[0]}.html", {
				'idol_arrays'  : [ data ],
			})
		
		sr_sets = [
			( "muse",       "µ's",        self.get_general_rotation(Group.Muse,       Rarity.SR)),
			( "aqours",     "Aqours",     self.get_general_rotation(Group.Aqours,     Rarity.SR)),
			( "nijigasaki", "Nijigasaki", self.get_general_rotation(Group.Nijigasaki, Rarity.SR)),
		]
		self._render_and_save("basic_rotation_template.html", "pages/sr_sets.html", {
			'grouped_rotations'  : sr_sets,
			'set_label' : 'Set',
		})
		
		ur_rotations = [
			( "muse",       "µ's",        self.get_general_rotation(Group.Muse,       Rarity.UR)),
			( "aqours",     "Aqours",     self.get_general_rotation(Group.Aqours,     Rarity.UR)),
			( "nijigasaki", "Nijigasaki", self.get_general_rotation(Group.Nijigasaki, Rarity.UR)),
		]
		self._render_and_save("basic_rotation_template.html", "pages/ur_rotations.html", {
			'grouped_rotations'  : ur_rotations,
			'set_label' : 'Rotation',
		})
		
		festival_rotations = [
			( "muse",       "µ's",        self.get_source_rotation(Group.Muse,       Source.Festival)),
			( "aqours",     "Aqours",     self.get_source_rotation(Group.Aqours,     Source.Festival)),
			( "nijigasaki", "Nijigasaki", self.get_source_rotation(Group.Nijigasaki, Source.Festival)),
		]
		self._render_and_save("basic_rotation_template.html", "pages/festival_rotations.html", {
			'grouped_rotations'  : festival_rotations,
			'set_label' : 'Rotation',
		})
		
		party_rotations = [
			( "muse",       "µ's",        self.get_source_rotation(Group.Muse,       Source.Party)),
			( "aqours",     "Aqours",     self.get_source_rotation(Group.Aqours,     Source.Party)),
			( "nijigasaki", "Nijigasaki", self.get_source_rotation(Group.Nijigasaki, Source.Party)),
		]
		self._render_and_save("basic_rotation_template.html", "pages/party_rotations.html", {
			'grouped_rotations'  : party_rotations,
			'set_label' : 'Rotation',
		})
		
		event_rotations = [
			( "muse",       "µ's",        self.get_source_rotation(Group.Muse,       Source.Event)),
			( "aqours",     "Aqours",     self.get_source_rotation(Group.Aqours,     Source.Event)),
			( "nijigasaki", "Nijigasaki", self.get_source_rotation(Group.Nijigasaki, Source.Event)),
		]
		self._render_and_save("basic_rotation_template.html", "pages/event_rotations.html", {
			'grouped_rotations'  : event_rotations,
			'set_label' : 'Rotation',
		})
		
		card_stats = self.get_card_stats();
		self._render_and_save("stats.html", "pages/stats.html", {
			'card_stats'  : card_stats,
		})
		
		# self._render_and_save("combined_layout.html", "index.html", {})
		

##################################

if __name__ == "__main__":
	cr = CardRotations()
	cr.generate_pages()

	print()
