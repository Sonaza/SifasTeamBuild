from operator import itemgetter
from enum import Enum
from typing import Dict, List
from IdolDatabase import *

client = KiraraClient()

class IdolError(Exception): pass

name_length = 25

# -------------------------------------------------------------

class IdolUnit(IdolBase):
	def __init__(self, card_ordinal : int, identifier : str, limit_break : int = 5):
		# super().__init__(idol.FullName, idol.School, idol.Year, idol.Subunit)
		
		self.data = client.get_idols_by_ordinal(card_ordinal, with_json=True)[0]
		
		idol = Idols.by_member_id[self.data.member_id]
		self.set(idol)
		
		self.member_id = self.data.member_id
		
		self.identifier 	= identifier
		
		if not (limit_break >= 0 and limit_break <= 5):
			raise IdolError("Limit break must be between 0-5")
			
		self.limit_break    = limit_break
		self._calculate_limit_break_values()
		
		self.accessories    = []
		
		self.bond_board = None
		self.song_modifier = None
		
		self.team_modifiers = [0, 0, 0]
		
		self._update_parameters()
	
	# ---------------------------------------------
	
	def _calculate_limit_break_values(self):
		# Map of values in tuples (tap skill, passive skill, max insights)
		values = {
			Source.Party : [
				(4, 5, 3), # LB 0
				(4, 5, 4), # LB 1
				(5, 5, 4), # LB 2
				(5, 6, 4), # LB 3
				(5, 6, 4), # LB 4
				(5, 7, 4), # LB 5
			],
			Source.Festival : [
				(3, 3, 3), # LB 0
				(3, 4, 3), # LB 1
				(3, 4, 3), # LB 2
				(4, 4, 3), # LB 3
				(4, 4, 4), # LB 4
				(5, 5, 4), # LB 5
			],
		}
		other = [
			(3, 3, 2), # LB 0
			(3, 4, 2), # LB 1
			(3, 4, 2), # LB 2
			(4, 4, 2), # LB 3
			(4, 4, 2), # LB 4
			(5, 5, 3), # LB 5
		]
		
		self.max_tap_skill_level, self.max_passive_skill_level, self.num_insight_slots = values.get(self.data.source, other)[self.limit_break]
	
	# ---------------------------------------------
	
	def set_team_modifiers(self, team_modifiers):
		self.team_modifiers = [0, 0, 0]
		for unit_modifiers in team_modifiers:
			self.team_modifiers = [sum(x) for x in zip(self.team_modifiers, unit_modifiers)]
		self._update_parameters()
		return self
	
	# ---------------------------------------------
	
	def add_accessories(self, accessories : Accessory):
		if isinstance(accessories, Accessory):
			self.accessories.append(accessories)
		elif isinstance(accessories, list):
			self.accessories.extend(accessories)
		else:
			raise ValueError("Expecting instance of Accessory or a list of Accessory instances.")
			
		assert(len(self.accessories) <= 3)
		self._update_parameters()
		return self
	
	# ---------------------------------------------
	
	def set_bond_board(self, bond_level, board_level, unlocked_tiles):
		self.bond_board = IdolBondBonuses.get_board_parameters(
			bond_level     = bond_level,
			board_level    = board_level,
			unlocked_tiles = unlocked_tiles)
		self._update_parameters()
		return self
	
	# ---------------------------------------------
	
	def set_song_modifiers(self, matching_attribute = Attribute.Unset, modifiers = (1, 1)):
		self.song_modifiers = (matching_attribute, modifiers[0], modifiers[1])
		self._update_parameters()
		return self
	
	# ---------------------------------------------
	
	def _update_parameters(self):
		if self.bond_board == None:
			self.raw_appeal, self.raw_stamina, self.raw_technique = self.data.get_raw_parameters(self.data.rarity.max_level, self.limit_break)
			self.base_appeal, self.base_stamina, self.base_technique = (self.raw_appeal, self.raw_stamina, self.raw_technique)
		else:
			bond_rarity_param = {
				Rarity.R  : BondParameter.RLevel,
				Rarity.SR : BondParameter.SRLevel,
				Rarity.UR : BondParameter.URLevel,
			}[self.data.rarity]
			self.raw_appeal, self.raw_stamina, self.raw_technique = self.data.get_raw_parameters(self.bond_board[bond_rarity_param], self.limit_break)
			# print("RAW", self.raw_appeal, self.raw_stamina, self.raw_technique)
			
			self.base_appeal    = self.raw_appeal    * (1 + self.bond_board[BondParameter.Appeal]    * 0.01)
			self.base_stamina   = self.raw_stamina   * (1 + self.bond_board[BondParameter.Stamina]   * 0.01)
			self.base_technique = self.raw_technique * (1 + self.bond_board[BondParameter.Technique] * 0.01)
		
		print(self.identifier, "BASE", self.base_appeal, self.base_stamina, self.base_technique)
		
		if self.song_modifier != None:
			if self.song_modifier[0] != Attribute.Unset:
				if self.song_modifier[0] == self.data.attribute:
					# On-attribute matching bonus
					matching_bonus = self.song_modifier[1]
					
					if self.bond_board != None:
						matching_bonus += self.bond_board[BondParameter.AttributeBonus] * 0.01
					
					self.base_appeal    *= matching_bonus
					self.base_stamina   *= matching_bonus
					self.base_technique *= matching_bonus
					
				elif self.song_modifier[0] != self.data.attribute:
					# Off-attribute song appeal penalty
					self.base_appeal    *= self.song_modifier[2]
		
		# Adjust insights, assuming best in slot appeal
		# num_insight_slots = self.data.data['max_passive_skill_slot']
		appeal_insight_skills = self.num_insight_slots * 2
		
		self.passive_multiplier = [0, 0, 0]
		passive_target, passive_effects = self.data.get_passive_skill_effect(self.max_passive_skill_level)
		if passive_target != SkillTarget.Group:
			for effect in passive_effects:
				if effect['target_parameter']   == SkillTargetParameter.Appeal:
					self.passive_multiplier[0] += effect['effect_value']
				elif effect['target_parameter'] == SkillTargetParameter.Stamina:
					self.passive_multiplier[1] += effect['effect_value']
				elif effect['target_parameter'] == SkillTargetParameter.Technique:
					self.passive_multiplier[2] += effect['effect_value']
		
		# Adjust appeal and technique per the buffs
		self.sheet_appeal    = math.floor(self.base_appeal)    * (1 + (self.passive_multiplier[0] + self.team_modifiers[0] + appeal_insight_skills) * 0.01)
		self.sheet_stamina   = math.floor(self.base_stamina)   * (1 + (self.passive_multiplier[1] + self.team_modifiers[1]) * 0.01)
		self.sheet_technique = math.floor(self.base_technique) * (1 + (self.passive_multiplier[2] + self.team_modifiers[2]) * 0.01)
		
		base_crit_power = 150
		crit_power_multiplier = 0
		
		for accessory in self.accessories:
			appeal, stamina, technique = accessory.get_parameters()
			self.sheet_appeal    += appeal
			self.sheet_stamina   += stamina
			self.sheet_technique += technique
			
			if accessory.attribute == self.data.attribute:
				self.sheet_appeal    += appeal * 0.1
				self.sheet_stamina   += stamina * 0.1
				self.sheet_technique += technique * 0.1
			
			if accessory.type == AccessoryType.Hairpin:
				base_crit_power += accessory.get_skill_value()
			elif accessory.type == AccessoryType.Bangle:
				crit_power_multiplier += accessory.get_skill_value()
		
		print(self.identifier, "SHEET", self.sheet_appeal, self.sheet_stamina, self.sheet_technique)
		
		#---------------------------------------------------------
		
		# Cards with technique as the highest stat get extra crit rate
		self.has_crit_sense   = (self.data.data['critical_rate_additive_bonus'] > 0)
		
		self.crit_rate = ((self.sheet_technique * 0.003) + (self.data.data['critical_rate_additive_bonus'] / 100)) * 0.01
		if self.bond_board != None:
			base_crit_power += self.bond_board[BondParameter.CritPower]
			self.crit_rate += self.bond_board[BondParameter.CritRate] * 0.01
		
		crit_power = base_crit_power * (1 + (crit_power_multiplier * 0.01))
		# print("final crit_power", crit_power)
		
		# Calculating the final value
		self.effective_appeal = (self.sheet_appeal * min(1, self.crit_rate) * (crit_power * 0.01)) + (self.sheet_appeal * (1 - min(1, self.crit_rate)))
	
	# ---------------------------------------------
	
	def __repr__(self):
		return f'IdolUnit({self.data.ordinal}, "{self.identifier}", {self.data.member_id})'
	
	def __str__(self):
		global name_length
		return f'{self.identifier + " " + self.first_name:<{name_length}}  |   {self.sheet_appeal:5.0f} appeal, {self.sheet_stamina:5.0f} stamina, {self.sheet_technique:5.0f} technique  |  {self.effective_appeal:5.0f} effective appeal |  Crit Rate {self.crit_rate * 100:5.2f}% ({[" ", "×"][int(self.has_crit_sense)]})'
		# return f'    {self.identifier + " " + self.first_name:<{name_length}}    Effective Appeal {self.effective_appeal:5.0f}    Crit Rate {self.crit_rate * 100:5.2f}% ({[" ", "×"][int(self.crit_sense)]})' 
		# return f'{self.identifier + " " + self.first_name:<{name_length}}  | {self.effective_appeal:5.0f}   | {self.crit_rate * 100:5.2f}% | ({[" ", "×"][int(self.crit_sense)]})' 
		
	def __lt__(self, other):
		return self.effective_appeal < other.effective_appeal

# -------------------------------------------------------------

class Strategy(Enum):
	Red   = 1
	Green = 2
	Blue  = 3

class IdolTeam():
	TEAM_PLACEMENT = [7, 5, 3, 1, 0, 2, 4, 6, 8]
	
	def __init__(self):
		self.units = dict.fromkeys(range(9), None)
		self.strategies = {
			Strategy.Red   : [7, 5, 3],
			Strategy.Green : [1, 0, 2],
			Strategy.Blue  : [4, 6, 8],
		}
		
		self.accessories = {
			Strategy.Red   : [],
			Strategy.Green : [],
			Strategy.Blue  : [],
		}
		
	def set_unit(self, placement : int, idolunit : IdolUnit):
		self.units[placement] = idolunit
		print(self.units)
	
	def set_all_units(self, idolunits : List[IdolUnit]):
		for placement, idolunit in zip(IdolTeam.TEAM_PLACEMENT, idolunits):
			self.units[placement] = idolunit
	
	def set_strategy_accessories(self, strategy : Strategy, accessories : List[Accessory]):
		assert(len(accessories) == 3)
		self.accessories[strategy] = accessories
		return self
	
	def set_accessories(self, accessories : Dict[Strategy, List[Accessory]]):
		for strategy, accessory_list in accessories.items():
			assert(len(accessory_list) == 3)
			self.accessories[strategy] = accessory_list
		
		print(self.accessories)
		return self
	
	def calculate_stats(self):
		pass

#########################################################

# idolunit = IdolUnit(728, "Fes3") # Nozomi
# idolunit.set_bond_board(**{ 'bond_level': 261, 'board_level': 260, 'unlocked_tiles' : True })

# idolunit.set_team_modifiers([
# 	# [7.0 + 8, 0, 0], # Kasu
# 	# [7.0 + 8, 0, 0], # Maru
# 	[8.4 + 8, 0, 4.2], # Koto
# 	[8.4 + 8, 0, 4.2], # Shio
	
# 	[4.2 + 8, 0, 0], # Rina
# 	[4.2 + 6, 0, 0], # Nozo
# 	[4.2 + 8, 0, 0], # Kanata
	
# 	[3.9 + 4, 0, 0], # Kanan
# 	[3.6 + 4, 0, 0], # Setsu
# 	[4.6 + 8, 0, 2.3], # Ransu
# ])

# print(idolunit)

the_best_team = IdolTeam()
the_best_team.set_all_units([
	# Fes2 Rina
	IdolUnit(487, "Fes2").set_bond_board(   **{ 'bond_level': 113, 'board_level': 60,  'unlocked_tiles' : [ BondParameter.Appeal, BondParameter.Technique, BondParameter.AttributeBonus ] }),
	# Magical Nozo
	IdolUnit(193, "Magical").set_bond_board(**{ 'bond_level': 261, 'board_level': 260, 'unlocked_tiles' : True }),
	# Fes1 Kanata
	IdolUnit(182, "Fes1").set_bond_board(   **{ 'bond_level': 120, 'board_level': 60,  'unlocked_tiles' : [ BondParameter.Appeal, BondParameter.AttributeBonus ] }),
	
	# Party Shio
	IdolUnit(477, "Party").set_bond_board(  **{ 'bond_level': 123, 'board_level': 120, 'unlocked_tiles' : [] }),
	# Fes3 Nozo
	IdolUnit(728, "Fes3").set_bond_board(   **{ 'bond_level': 261, 'board_level': 260, 'unlocked_tiles' : True }),
	# Party Koto
	IdolUnit(514, "Party").set_bond_board(  **{ 'bond_level': 91,  'board_level': 60,  'unlocked_tiles' : [ BondParameter.Appeal, BondParameter.Technique, BondParameter.AttributeBonus ] }),
	
	# Initial Kanan
	IdolUnit(48, "Initial").set_bond_board( **{ 'bond_level': 108, 'board_level': 60, 'unlocked_tiles'  : [] }),
	# Star Setsu
	IdolUnit(713, "Star").set_bond_board(   **{ 'bond_level': 81,  'board_level': 40,  'unlocked_tiles' : [ BondParameter.CritRate ] }),
	# Party Ransu
	IdolUnit(629, "Party").set_bond_board(  **{ 'bond_level': 50,  'board_level': 30,  'unlocked_tiles' : [] }),
	
	# # Fes3 Nozo
	# IdolUnit(728, "Fes3").set_bond_board(**{ 'bond_level': 261, 'board_level': 260, 'unlocked_tiles' : [ BondParameter.AttributeBonus ] }),
])

the_best_team.set_accessories({
	Strategy.Green : [
		Accessories.Bangle.get(Attribute.Pure,    Rarity.UR),
		Accessories.Bangle.get(Attribute.Active,  Rarity.UR),
		Accessories.Brooch.get(Attribute.Natural, Rarity.UR),
	],
	Strategy.Red : [
		Accessories.Belt.get(Attribute.Cool,      Rarity.UR),
		Accessories.Belt.get(Attribute.Natural,   Rarity.UR),
		Accessories.Bracelet.get(Attribute.Smile, Rarity.UR),
	],
	Strategy.Blue : [
		Accessories.Bracelet.get(Attribute.Active, Rarity.UR),
		Accessories.Bracelet.get(Attribute.Active, Rarity.UR),
		Accessories.Bracelet.get(Attribute.Active, Rarity.UR),
	],
})

# idolunit.set_bond_board(**{ 'bond_level': 300, 'board_level': 300, 'unlocked_tiles' : True })

# print(idolunit)
