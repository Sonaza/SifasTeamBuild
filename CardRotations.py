from operator import itemgetter
from enum import Enum
from collections import defaultdict

from IdolDatabase import *
from IdolKiraraClient import KiraraClient

client = KiraraClient()

group = Group.Nijigasaki

#####

idols = client.get_idols_by_group(group, Rarity.UR)

default_group_list = dict()
for idol in Idols.by_group[group]:
	default_group_list[idol.member_id] = None

num_rotations = 0
cards_per_girl = defaultdict(list)
for idol in idols:
	cards_per_girl[idol.member_id].append(idol)
	
for girl, cards in cards_per_girl.items():
	print(f"{Idols.by_member_id[girl].first_name:>10} has {len(cards):>2} URs")
	num_rotations = max(num_rotations, len(cards))

rotations = []
for rotation_index in range(num_rotations):
	current_rotation = dict(default_group_list)

	for girl, cards in cards_per_girl.items():
		if rotation_index < len(cards):
			current_rotation[girl] = cards[rotation_index]
		else:
			current_rotation[girl] = None
	
	rotations.append(current_rotation)
	rotation_index += 1

##################################

for index, card_rotation in enumerate(rotations):
	print(f"Card rotation {index + 1}:")
	print("  ")
	for girl, card in card_rotation.items():
		if card:
			print(card)
		else:
			print(f"Still missing: {Idols.by_member_id[girl].first_name}")
	
	print()

print()
