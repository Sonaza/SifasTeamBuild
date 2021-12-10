from operator import itemgetter
from enum import Enum
from collections import defaultdict

from IdolDatabase import *
from IdolKiraraClient import KiraraClient

client = KiraraClient()

class CardRotations():
	
	member_delays = dict([
		# (210, 3), # Shioriko
		# (212, 8), # Ransu
		# (211, 8), # Mia
	])
	
	member_order = [
		8, 5, 6, # First years
		1, 3, 4, # Second years
		7, 2, 9, # Third years

		107, 106, 109, # First years
		101, 102, 105, # Second years
		103, 104, 108, # Third years

		203, 202, 209, 210, # First years
		201, 207, 205, 212, # Second years
		208, 206, 204, 211, # Third years
	]
	
	def __init__(self):
		pass
		
	def sort_rotation(self, rotation):
		output = []
		for ordered_member_id in CardRotations.member_order:
			if ordered_member_id in rotation:
				output.append((ordered_member_id, rotation[ordered_member_id]))
				
		return output
	
	def get_general_rotation(self, group : Group, rarity : Rarity):
		num_rotations = 0
		cards_per_girl = defaultdict(list)

		default_group_list = dict()
		for idol in Idols.by_group[group]:
			default_group_list[idol.member_id] = None
			
			if idol.member_id in CardRotations.member_delays:
				cards_per_girl[idol.member_id].extend([None] * CardRotations.member_delays[idol.member_id])

		idols = client.get_idols_by_group(group, rarity)
		for idol in idols:
			cards_per_girl[idol.member_id].append(idol)
			
		for member_id, cards in cards_per_girl.items():
			print(f"{Idols.by_member_id[member_id].first_name:>10} has {len(cards):>2} URs")
			num_rotations = max(num_rotations, len(cards))

		rotations = []
		for rotation_index in range(num_rotations):
			current_rotation = dict(default_group_list)

			for member_id, cards in cards_per_girl.items():
				if rotation_index < len(cards):
					current_rotation[member_id] = cards[rotation_index]
				else:
					current_rotation[member_id] = None
			
			rotations.append(self.sort_rotation(current_rotation))
			rotation_index += 1
		
		return rotations

##################################

cr = CardRotations()
rotations = cr.get_general_rotation(Group.Muse, Rarity.UR)

for index, card_rotation in enumerate(rotations):
	print(f"Card rotation {index + 1}:")
	print("  ")
	for member_id, card in card_rotation:
		if card:
			# print(card)
			print(f'<div class="grid-icon idol-{member_id}"><a href="https://allstars.kirara.ca/card/{card.ordinal}"><img src="{card.data["normal_appearance"]["thumbnail_asset_path"]}" alt=""></a></div>')
		else:
			print(f'<div class="grid-icon idol-{member_id} missing"></div>')
			# if member_id in CardRotations.member_delays and index < CardRotations.member_delays[member_id]:
			# 	pass
			# else:
			# 	print(f"Still missing: {Idols.by_member_id[member_id].first_name}")
	
	print()

print()
