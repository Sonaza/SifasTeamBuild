import Config
from IdolDatabase import *

from CardRotations import GeneratorBase, CardValidity
from ..Utility import Utility

from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

from ..RotationsData import GeneralData, SRSetsData

class BasicRotationsGenerator(GeneratorBase):
	def __init__(self, parent):
		super().__init__(parent)
	
	used_templates = ["deferred_rotation.html", "deferred_card_grid.html"]
	
	def render_deferred_card_grids(self, rotation_set_label, grouped_rotations):
		for group, group_data in grouped_rotations:
			for rotation_index, card_rotation, rotation_title in group_data:
				self.render_and_save("deferred_card_grid.html", f"pages/deferred/{rotation_set_label}_{group.tag}_{rotation_index}.html", {
					'rotation_index'     : rotation_index,
					'card_rotation'      : card_rotation,
				}, minify_html=not self.args.dev)
		
	def generate_and_render(self):
		# General UR rotations
		ur_rotations = [(group, self.get_general_rotation(group, Rarity.UR)) for group in Group]
		self.render_and_save("deferred_rotation.html", "pages/ur_rotations.html", {
			'grouped_rotations'  : ur_rotations,
			'rotation_set_label' : 'ur',
			'set_label'          : 'Rotation',
			'page_title'         : 'UR Rotations',
			'page_description'   : '''Rotations for all UR cards. <b>Please note:</b> these rotations are automatically laid in the original release
			                          order and manual per-rotation exceptions are not planned for this page beyond adjusting the initial URs.''',
		}, minify_html=not self.args.dev)
		self.render_deferred_card_grids('ur', ur_rotations)
	
		# Festival UR rotations
		festival_rotations = [(group, self.get_source_rotation(group, Source.Festival)) for group in Group]
		self.render_and_save("deferred_rotation.html", "pages/festival_rotations.html", {
			'grouped_rotations'  : festival_rotations,
			'rotation_set_label' : 'festival',
			'set_label'          : 'Rotation',
			'page_title'         : 'Festival UR Rotations',
			'page_description'   : 'Rotations for Festival limited URs scouted exclusively from All Stars Festival banners.',
		}, minify_html=not self.args.dev)
		self.render_deferred_card_grids('festival', festival_rotations)
	
		# Party UR rotations
		party_rotations = [(group, self.get_source_rotation(group, Source.Party)) for group in Group]
		self.render_and_save("deferred_rotation.html", "pages/party_rotations.html", {
			'grouped_rotations'  : party_rotations,
			'rotation_set_label' : 'party',
			'set_label'          : 'Rotation',
			'page_title'         : 'Party UR Rotations',
			'page_description'   : 'Rotations for Party limited URs scouted exclusively from Party Scouting banners.',
		}, minify_html=not self.args.dev)
		self.render_deferred_card_grids('party', party_rotations)
	
		# Event UR rotations
		event_rotations = [(group, self.get_source_rotation(group, Source.Event)) for group in Group]
		self.render_and_save("deferred_rotation.html", "pages/event_rotations.html", {
			'grouped_rotations'  : event_rotations,
			'rotation_set_label' : 'event',
			'set_label'          : 'Rotation',
			'page_title'         : 'Event UR Rotations',
			'page_description'   : 'Rotations for Event URs awarded in item exchange and story events.',
		}, minify_html=not self.args.dev)
		self.render_deferred_card_grids('event', event_rotations)
	
		# SR Sets
		sr_sets = [(group, self.get_sr_sets(group)) for group in Group]
		self.render_and_save("deferred_rotation.html", "pages/sr_sets.html", {
			'grouped_rotations'  : sr_sets,
			'rotation_set_label' : 'sr',
			'set_label'          : 'Set',
			'page_title'         : 'SR Sets',
			'page_description'   : '''SR cards organised into sets by costume or other common theme.''',
		}, minify_html=not self.args.dev)
		self.render_deferred_card_grids('sr', sr_sets)
		return True

	# -------------------------------------------------------------------------------------------
	
	def get_general_rotation(self, group : Group, rarity : Rarity):
		cards_per_girl = defaultdict(list)

		default_group_list = dict()
		for idol in Idols.by_group[group]:
			default_group_list[idol.member_id] = None
			
			if idol.member_id in GeneralData.member_delays_by_rarity[rarity]:
				if isinstance(GeneralData.member_delays_by_rarity[rarity][idol.member_id], int):
					cards_per_girl[idol.member_id].extend([CardValidity.CardNonExtant()] * GeneralData.member_delays_by_rarity[rarity][idol.member_id])
				else:
					cards_per_girl[idol.member_id].extend([CardValidity.CardNonExtant()] * GeneralData.member_delays_by_rarity[rarity][idol.member_id][0])
					GeneralData.member_delays_by_rarity[rarity][idol.member_id] = GeneralData.member_delays_by_rarity[rarity][idol.member_id][1:]
					

		idols = self.client.get_idols(group=group, rarity=rarity)
		for idol in idols:
			cards_per_girl[idol.member_id].append(idol)
			
			if idol.member_id in GeneralData.member_delays_by_rarity[rarity]:
				if isinstance(GeneralData.member_delays_by_rarity[rarity][idol.member_id], list) and len(GeneralData.member_delays_by_rarity[rarity][idol.member_id]) > 0:
					cards_per_girl[idol.member_id].extend([CardValidity.CardNonExtant()] * GeneralData.member_delays_by_rarity[rarity][idol.member_id][0])
					GeneralData.member_delays_by_rarity[rarity][idol.member_id] = GeneralData.member_delays_by_rarity[rarity][idol.member_id][1:]
			
		num_rotations = 0
		for member_id, cards in cards_per_girl.items():
			num_rotations = max(num_rotations, len(cards))

		rotations = []
		for rotation_index in range(num_rotations):
			current_rotation = dict(default_group_list)
			
			try:
				set_title = GeneralData.set_title_overrides[rarity][group][rotation_index]
			except KeyError:
				set_title = None
			
			titles = defaultdict(int)
			
			for idol in Idols.by_group[group]:
				if idol.member_id not in cards_per_girl:
					current_rotation[idol.member_id] = CardValidity.CardMissing()
				else:
					cards = cards_per_girl[idol.member_id]
					if rotation_index < len(cards):
						current_rotation[idol.member_id] = cards[rotation_index]
						
						if set_title == None and rarity == Rarity.SR and CardValidity.is_valid_card(cards[rotation_index]):
							t = cards[rotation_index].get_card_name(True)
							titles[t] += 1
					else:
						current_rotation[idol.member_id] = CardValidity.CardMissing()
			
			if titles:
				titles = sorted(titles.items(), key=itemgetter(1), reverse=True)
				if len(titles) == 1 or titles[0][1] > 1:
					set_title = titles[0][0]
				else:
					print("WARNING! No set name could be determined for", rarity, group, "index", rotation_index)
		
			rotations.append(( rotation_index, Utility.sort_by_key_order(current_rotation, Idols.member_order_by_group[group]), set_title ))
		
		return list(reversed(rotations))
	
	# -------------------------------------------------------------------------------------------
	
	def get_sr_sets(self, group : Group):
		idolized_same_set = SRSetsData.idolized_same_set.get(group, {})
		idolized_same_set = {title.strip(): set_title for set_title, idolized_titles in idolized_same_set.items() for title in idolized_titles}
		skipped_sets      = SRSetsData.skipped_sets.get(group, {})
		
		current_set_index = 0
		set_indexes = []
		idol_sets = defaultdict(dict)
		
		idols = self.client.get_idols(group=group, rarity=Rarity.SR)
		for idol in idols:
			title = idol.get_card_name(True)
			title = idolized_same_set.get(title, title)
			if title not in idol_sets:
				# print(title.encode('utf-8'))
				set_indexes.append((current_set_index, title))
				current_set_index += 1
			
			idol_sets[title][idol.member_id] = idol
		
		rotations = []
		for rotation_index, set_title in set_indexes:
			current_rotation = {}
			for member in Idols.member_order_by_group[group]:
				if member in idol_sets[set_title]:
					# Card found, add to rotation
					current_rotation[member] = idol_sets[set_title][member]
					
				elif member in skipped_sets and rotation_index in skipped_sets[member]:
					# Card is explicitly skipped
					current_rotation[member] = CardValidity.CardNonExtant()
					
				else:
					# Card not yet added to the game
					current_rotation[member] = CardValidity.CardMissing()
			
			rotations.append(( rotation_index, Utility.sort_by_key_order(current_rotation, Idols.member_order_by_group[group]), set_title ))
		
		return list(reversed(rotations))
	
	# -------------------------------------------------------------------------------------------
	
	def get_source_rotation(self, group : Group, source : Source):
		cards_per_girl = defaultdict(list)

		default_group_list = dict()
		for idol in Idols.by_group[group]:
			default_group_list[idol.member_id] = None
			
			try:
				cards_per_girl[idol.member_id].extend([CardValidity.CardNonExtant()] * GeneralData.member_delays_by_source[source][idol.member_id])
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
					current_rotation[idol.member_id] = CardValidity.CardMissing()
				else:
					cards = cards_per_girl[idol.member_id]
					if rotation_index < len(cards):
						current_rotation[idol.member_id] = cards[rotation_index]
					else:
						current_rotation[idol.member_id] = CardValidity.CardMissing()
			
			rotations.append(( rotation_index, Utility.sort_by_key_order(current_rotation, Idols.member_order_by_group[group]), None ))
		
		return list(reversed(rotations))
		
