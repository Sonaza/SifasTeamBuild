from operator import itemgetter
from enum import Enum
from collections import defaultdict

from IdolDatabase import *
from IdolKiraraClient import KiraraClient, KiraraIdol

import os
import time
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
		num_atlases = 0
		sizes = [80]
		
		for group in Group:
			cards = self.client.get_idols_by_group(group, Rarity.UR)
			cards_per_girl = defaultdict(list)
			for card in cards:
				cards_per_girl[card.member_id].append(card)
			
			num_rotations = 0
			num_members = len(Idols.by_group[group])
			for member_id, cards in cards_per_girl.items():
				num_rotations = max(num_rotations, len(cards))
			
			print(group, num_rotations, num_members)
			
			for size in sizes:
				thumbnail_size = (size, size)
				image_size = (thumbnail_size[0] * num_members, thumbnail_size[1] * num_rotations)
				atlas_normal = Image.new('RGB', image_size, (0, 0, 0,))
				atlas_idolized = Image.new('RGB', image_size, (0, 0, 0,))
				
				for column_index, ordered_member_id in enumerate(Idols.member_order[group]):
					for row_index, card in enumerate(cards_per_girl[ordered_member_id]):
						target_coordinates = (thumbnail_size[0] * column_index, thumbnail_size[1] * row_index)
						
						atlas_by_ordinal[card.ordinal] = (group, 0, target_coordinates)
						
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
					
				atlas_normal.save(f'output/thumbnails/atlas_{group.value}_0_normal.png', 'PNG')
				atlas_idolized.save(f'output/thumbnails/atlas_{group.value}_0_idolized.png', 'PNG')
				
		groups = []
		for group in Group:
			for atlas_index in range(num_atlases + 1):
				groups.append(f".using-normal-thumbnails   .card-thumbnail.group-{group.value} {{ background: url('thumbnails/atlas_{group.value}_{atlas_index}_normal.png') no-repeat; }}")
				groups.append(f".using-idolized-thumbnails .card-thumbnail.group-{group.value} {{ background: url('thumbnails/atlas_{group.value}_{atlas_index}_idolized.png') no-repeat; }}")
				
		with open("output/atlas.css", "w", encoding="utf8") as f:
			for line in groups:
				f.write(line + "\n")
			
			for ordinal, (group, atlas_index, coordinates) in atlas_by_ordinal.items():
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
		
		# self.thumbnails = CardThumbnails(self.client)
		
		# if self.thumbnails.download_thumbnails():
		# 	self.thumbnails.make_atlas()
		
	def _sort_rotation(self, group, rotation):
		output = []
		for ordered_member_id in Idols.member_order[group]:
			if ordered_member_id in rotation:
				output.append((ordered_member_id, rotation[ordered_member_id]))
		
		return output
	
	def get_general_rotation(self, group : Group, rarity : Rarity):
		member_delays = dict([
			(Member.Shioriko, 3),
			(Member.Lanzhu,   7),
			(Member.Mia,      7),
		])
		
		cards_per_girl = defaultdict(list)

		default_group_list = dict()
		for idol in Idols.by_group[group]:
			default_group_list[idol.member_id] = None
			
			if idol.member_id in member_delays:
				cards_per_girl[idol.member_id].extend([CardNonExtant()] * member_delays[idol.member_id])

		idols = self.client.get_idols_by_group(group, rarity)
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
			
			rotations.append(self._sort_rotation(group, current_rotation))
			rotation_index += 1
		
		return rotations
	
	def get_limited_rotation(self, group : Group, source : Source):
		member_delays = dict([
			(Member.Shioriko, 3),
			(Member.Lanzhu,   7),
			(Member.Mia,      7),
		])
		
		cards_per_girl = defaultdict(list)

		default_group_list = dict()
		for idol in Idols.by_group[group]:
			default_group_list[idol.member_id] = None
			
			# if idol.member_id in member_delays:
			# 	cards_per_girl[idol.member_id].extend([CardNonExtant()] * member_delays[idol.member_id])

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
			
			rotations.append(self._sort_rotation(group, current_rotation))
			rotation_index += 1
		
		return rotations
		
	def _render_and_save(self, template_path, output_path, data):
		# template = self.jinja.get_template(os.path.join("templates", template_path).replace("\\","/"))
		template = self.jinja.get_template(template_path)
		rendered_output = template.render(data)
		
		with open(os.path.join("output", output_path), "w", encoding="utf8") as f:
			f.write(rendered_output)
			f.close()
	
	def generate_pages(self):
		def include_page(filepath):
			filepath = os.path.join("output", filepath)
			if not os.path.exists(filepath): return f"<h1>Error: {filepath} does not exist.</h1>"
			with open(filepath, encoding="utf8") as f:
				return f.read()
			return f"<h1>Error: Failed to open {filepath}.</h1>"
		
		self.jinja.globals.update({
			'Idols' : Idols,
			
			'is_valid_card':     is_valid_card,
			'is_missing_card':   is_missing_card,
			'is_nonextant_card': is_nonextant_card,
			
			'ordinalize'    : ordinalize,
			'include'       : include_page,
		})
		
		ur_rotations = [
			( "muse",       "µ's",        self.get_general_rotation(Group.Muse,       Rarity.UR), ),
			( "aqours",     "Aqours",     self.get_general_rotation(Group.Aqours,     Rarity.UR), ),
			( "nijigasaki", "Nijigasaki", self.get_general_rotation(Group.Nijigasaki, Rarity.UR), ),
		]
		self._render_and_save("basic_rotation_template.html", "ur_rotations.html", {
			'grouped_rotations'  : ur_rotations
		})
		
		festival_rotations = [
			( "muse",       "µ's",        self.get_limited_rotation(Group.Muse,       Source.Festival)),
			( "aqours",     "Aqours",     self.get_limited_rotation(Group.Aqours,     Source.Festival)),
			( "nijigasaki", "Nijigasaki", self.get_limited_rotation(Group.Nijigasaki, Source.Festival)),
		]
		self._render_and_save("basic_rotation_template.html", "festival_rotations.html", {
			'grouped_rotations'  : festival_rotations
		})
		
		party_rotations = [
			( "muse",       "µ's",        self.get_limited_rotation(Group.Muse,       Source.Party)),
			( "aqours",     "Aqours",     self.get_limited_rotation(Group.Aqours,     Source.Party)),
			( "nijigasaki", "Nijigasaki", self.get_limited_rotation(Group.Nijigasaki, Source.Party)),
		]
		self._render_and_save("basic_rotation_template.html", "party_rotations.html", {
			'grouped_rotations'  : party_rotations
		})
		
		self._render_and_save("combined_layout.html", "index.html", {})
		

##################################

cr = CardRotations()
cr.generate_pages()

print()
