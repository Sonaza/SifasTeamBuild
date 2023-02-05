from operator import itemgetter
from enum import Enum
from typing import Dict, List
from IdolDatabase import *
from dataclasses import dataclass

client = KiraraClient()

class IdolError(Exception): pass

name_length = 25

# -------------------------------------------------------------

@dataclass
class InsightSkill:
	skill_target  : SkillTarget
	effect_type   : SkillEffectType
	effect_value  : float

class InsightSkills():
	Appeal_S_All       = InsightSkill(SkillTarget.All,            SkillEffectType.AddAppealBase, effect_value = 1.0)
	Appeal_S_Strategy  = InsightSkill(SkillTarget.SameStrategy,   SkillEffectType.AddAppealBase, effect_value = 1.0)
	Appeal_M_Strategy  = InsightSkill(SkillTarget.SameStrategy,   SkillEffectType.AddAppealBase, effect_value = 2.0)
	Appeal_S_Group     = InsightSkill(SkillTarget.Group,          SkillEffectType.AddAppealBase, effect_value = 1.0)
	Appeal_M_Group     = InsightSkill(SkillTarget.Group,          SkillEffectType.AddAppealBase, effect_value = 2.0)
	Appeal_S_Attribute = InsightSkill(SkillTarget.SameAttribute,  SkillEffectType.AddAppealBase, effect_value = 1.0)
	Appeal_M_Attribute = InsightSkill(SkillTarget.SameAttribute,  SkillEffectType.AddAppealBase, effect_value = 2.0)
	Appeal_S_Year      = InsightSkill(SkillTarget.SameYear,       SkillEffectType.AddAppealBase, effect_value = 1.0)
	Appeal_M_Year      = InsightSkill(SkillTarget.SameYear,       SkillEffectType.AddAppealBase, effect_value = 2.0)
	Appeal_S_School    = InsightSkill(SkillTarget.SameSchool,     SkillEffectType.AddAppealBase, effect_value = 1.0)
	Appeal_M_School    = InsightSkill(SkillTarget.SameSchool,     SkillEffectType.AddAppealBase, effect_value = 2.0)

@dataclass
class SongInfo:
	song_attribute    : Attribute
	
	gimmick_target_attributes : List[Attribute] 
	gimmick_effect_type       : SkillEffectType
	gimmick_effect_value      : float
	
	@staticmethod
	def make_attribute_gimmick(song_attribute : Attribute, effect_type : SkillEffectType, effect_value : float):
		return SongInfo(
			song_attribute            = song_attribute,
			gimmick_target_attributes = [attribute for attribute in Attribute.get_valid() if attribute != song_attribute],
			gimmick_effect_type       = effect_type,
			gimmick_effect_value      = effect_value,
		)
		

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

		self.insight_skills = []
		self.accessories    = []

		self.bond_board = None
		self.song_info = None
		self.team_modifiers = [0, 0, 0]
		
		self.max_level = self.data.rarity.max_level

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
		# self.team_modifiers = [0, 0, 0]
		self.team_modifiers = team_modifiers
		# for unit_modifiers in team_modifiers:
		# 	self.team_modifiers = [sum(x) for x in zip(self.team_modifiers, unit_modifiers)]
		self._update_parameters()
		return self

	# ---------------------------------------------

	def set_accessories(self, accessories : Accessory):
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
	
	def set_insight_skills(self, insights : List[InsightSkill]):
		assert(len(insights) >= 0 and len(insights) <= 4)
		self.insight_skills = insights
		return self
	
	# ---------------------------------------------

	def set_bond_board(self, bond_level, board_level, unlocked_tiles):
		self.bond_board = IdolBondBonuses.get_board_parameters(
			bond_level     = bond_level,
			board_level    = board_level,
			unlocked_tiles = unlocked_tiles)
		
		bond_rarity_param = {
			Rarity.R  : BondParameter.RLevel,
			Rarity.SR : BondParameter.SRLevel,
			Rarity.UR : BondParameter.URLevel,
		}[self.data.rarity]
		self.max_level = self.bond_board[bond_rarity_param]
		
		self._update_parameters()
		return self

	# ---------------------------------------------

	def set_song_info(self, song_info : SongInfo):
		self.song_info = song_info
		self._update_parameters()
		return self

	# ---------------------------------------------

	def _update_parameters(self):
		if self.bond_board == None:
			self.raw_appeal, self.raw_stamina, self.raw_technique = self.data.get_raw_parameters(self.max_level, self.limit_break)
			self.base_appeal, self.base_stamina, self.base_technique = (self.raw_appeal, self.raw_stamina, self.raw_technique)
		else:
			self.raw_appeal, self.raw_stamina, self.raw_technique = self.data.get_raw_parameters(self.max_level, self.limit_break)
			# print("RAW", self.raw_appeal, self.raw_stamina, self.raw_technique)

			self.base_appeal    = self.raw_appeal    * (1 + self.bond_board[BondParameter.Appeal]    * 0.01)
			self.base_stamina   = self.raw_stamina   * (1 + self.bond_board[BondParameter.Stamina]   * 0.01)
			self.base_technique = self.raw_technique * (1 + self.bond_board[BondParameter.Technique] * 0.01)

		# print(self.identifier, "BASE", self.base_appeal, self.base_stamina, self.base_technique)

		# Adjust stats per the buffs
		self.sheet_appeal    = math.floor(self.base_appeal)    * (1 + (self.team_modifiers[0]) * 0.01)
		self.sheet_stamina   = math.floor(self.base_stamina)   * (1 + (self.team_modifiers[1]) * 0.01)
		self.sheet_technique = math.floor(self.base_technique) * (1 + (self.team_modifiers[2]) * 0.01)

		base_crit_power = 150
		crit_power_multiplier = 0

		for accessory in self.accessories:
			AddAppealBase, stamina, technique = accessory.get_parameters()
			self.sheet_appeal    += AddAppealBase
			self.sheet_stamina   += stamina
			self.sheet_technique += technique

			if accessory.attribute == self.data.attribute:
				self.sheet_appeal    += AddAppealBase * 0.1
				self.sheet_stamina   += stamina * 0.1
				self.sheet_technique += technique * 0.1

			if accessory.type == AccessoryType.Hairpin:
				base_crit_power += accessory.get_skill_value()
			elif accessory.type == AccessoryType.Bangle:
				crit_power_multiplier += accessory.get_skill_value()
			
		self.sheet_appeal    = int(self.sheet_appeal)
		self.sheet_stamina   = int(self.sheet_stamina)
		self.sheet_technique = int(self.sheet_technique)
		
		if self.song_info != None:
			# Attribute matching bonus
			if self.song_info.song_attribute == self.data.attribute:
				# Base matching bonus is +20% to all stats
				matching_bonus = 1.2
				
				if self.bond_board != None:
					matching_bonus += self.bond_board[BondParameter.AttributeBonus] * 0.01
					
				self.sheet_appeal    *= matching_bonus
				self.sheet_stamina   *= matching_bonus
				self.sheet_technique *= matching_bonus
			
			# Song Gimmick
			if self.data.attribute in self.song_info.gimmick_target_attributes:
				if self.song_info.gimmick_effect_type == SkillEffectType.ReduceAppealBaseBonus:
					self.sheet_appeal    *= (1 - self.song_info.gimmick_effect_value)
				else:
					raise Exception("Not implemented: " + self.song_info.gimmick_effect_type)
					
		self.sheet_appeal    = int(self.sheet_appeal)
		self.sheet_stamina   = int(self.sheet_stamina)
		self.sheet_technique = int(self.sheet_technique)
		
		# print(self.identifier, "SHEET", self.sheet_appeal, self.sheet_stamina, self.sheet_technique)

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
	
	def get_identifier(self):
		return f'{self.identifier + " " + self.first_name}'
	
	def __repr__(self):
		return f'IdolUnit({self.data.ordinal}, "{self.identifier}", {self.data.member_id})'

	def __str__(self):
		global name_length
		return f'{self.identifier + " " + self.first_name:<{name_length}} Lv.{self.max_level} (LB{self.limit_break}) |   {self.sheet_appeal:5d} appeal, {self.sheet_stamina:5d} stamina, {self.sheet_technique:5d} technique  |  {self.effective_appeal:6.0f} effective appeal |  Crit Rate {self.crit_rate * 100:5.2f}% ({[" ", "×"][int(self.has_crit_sense)]})'
		# return f'    {self.identifier + " " + self.first_name:<{name_length}}    Effective appeal {self.effective_appeal:5.0f}    Crit Rate {self.crit_rate * 100:5.2f}% ({[" ", "×"][int(self.crit_sense)]})'
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
		return self

	def get_units_per_strategy(self):
		output = {}
		for strategy, placements in self.strategies.items():
			output[strategy] = [self.units[x] for x in placements]
		return output

	def get_unit_strategy(self, unit_index : int):
		for strategy, placements in self.strategies.items():
			if unit_index in placements:
				return strategy
		raise IdolError("Check your values! Unit index does not exist in any strategy!")

	def test_if_skill_applies(self, skill_target : SkillTarget, unit_index_a : int, unit_index_b  : int):
		if skill_target == SkillTarget.All:
			return True
		elif skill_target == SkillTarget.Group:
			return unit_index_a != unit_index_b
		elif skill_target == SkillTarget.Self:
			return unit_index_a == unit_index_b
		elif skill_target == SkillTarget.SameStrategy:
			return self.get_unit_strategy(unit_index_a) == self.get_unit_strategy(unit_index_b)
			
		unit_a = self.units[unit_index_a]
		unit_b = self.units[unit_index_b]
	
		if skill_target == SkillTarget.SameAttribute:
			return unit_a.data.attribute == unit_b.data.attribute
		elif skill_target == SkillTarget.SameYear:
			return unit_a.member_id.year == unit_b.member_id.year
		elif skill_target == SkillTarget.SameSchool:
			return unit_a.member_id.group == unit_b.member_id.group
		elif skill_target == SkillTarget.SameType:
			return unit_a.data.type == unit_b.data.type
		elif skill_target == SkillTarget.SameMember:
			return unit_a.member_id == unit_b.member_id
		elif skill_target == SkillTarget.SameSubunit:
			return unit_a.member_id.subunit == unit_b.member_id.subunit
		
		raise IdolError("Something was not tested")
			
	def calculate_stats(self, song_info : Optional[SongInfo] = None):
		self.units_per_strategy = self.get_units_per_strategy()

		for strategy, units in self.units_per_strategy.items():
			for unit in units:
				unit.set_accessories(self.accessories[strategy])
		
		passive_multipliers = {}
		passive_multiplier = [0, 0, 0]
		
		for unit_a_index, unit_a in self.units.items():
			passive_target, passive_effects = unit_a.data.get_passive_skill_effect(unit_a.max_passive_skill_level) 
			for unit_b_index, unit_b in self.units.items():
				if unit_b_index not in passive_multipliers:
					passive_multipliers[unit_b_index] = [0, 0, 0]
				
				skill_applies = self.test_if_skill_applies(passive_target, unit_a_index, unit_b_index)
				if skill_applies:
					for effect in passive_effects:
						if effect.effect_type   == SkillEffectType.AddAppealBase:
							passive_multipliers[unit_b_index][0] += effect.effect_value
						elif effect.effect_type == SkillEffectType.AddStaminaBase:
							passive_multipliers[unit_b_index][1] += effect.effect_value
						elif effect.effect_type == SkillEffectType.AddTechniqueBase:
							passive_multipliers[unit_b_index][2] += effect.effect_value
				
				for skill in unit_a.insight_skills:
					skill_applies = self.test_if_skill_applies(skill.skill_target, unit_a_index, unit_b_index)
					# print(skill, unit_a_index, unit_b_index)
					if skill_applies:
						if skill.effect_type   == SkillEffectType.AddAppealBase:
							passive_multipliers[unit_b_index][0] += skill.effect_value
						elif skill.effect_type == SkillEffectType.AddStaminaBase:
							passive_multipliers[unit_b_index][1] += skill.effect_value
						elif skill.effect_type == SkillEffectType.AddTechniqueBase:
							passive_multipliers[unit_b_index][2] += skill.effect_value
		
		for unit_index, multipliers in passive_multipliers.items():
			self.units[unit_index].set_team_modifiers(multipliers)
			self.units[unit_index].set_song_info(song_info)
			
			# print(self.units[unit_index].get_identifier(), multipliers)
		
		for strategy, units in self.units_per_strategy.items():
			print(f"{strategy}")
			for unit in units:
				print(f"   {unit}")
			print()

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
	IdolUnit(487, "Fes2", limit_break = 5) \
		.set_bond_board(**{ 'bond_level': 113, 'board_level': 60,  'unlocked_tiles' : [ BondParameter.Appeal, BondParameter.Technique, BondParameter.AttributeBonus ] }) \
	    .set_insight_skills([InsightSkills.Appeal_M_Group] * 4),
	# Magical Nozo
	IdolUnit(193, "Magical", limit_break = 5) \
		.set_bond_board(**{ 'bond_level': 261, 'board_level': 260, 'unlocked_tiles' : True }) \
		.set_insight_skills([InsightSkills.Appeal_M_Group] * 3),
	# Fes1 Kanata
	IdolUnit(182, "Fes1", limit_break = 5) \
		.set_bond_board(**{ 'bond_level': 120, 'board_level': 60,  'unlocked_tiles' : [ BondParameter.Appeal, BondParameter.AttributeBonus ] }) \
	    .set_insight_skills([InsightSkills.Appeal_M_Group] * 4),

	# # Party Shio
	# IdolUnit(477, "Party", limit_break = 5) \
	# 	.set_bond_board(**{ 'bond_level': 123, 'board_level': 120, 'unlocked_tiles' : [] }) \
	#     .set_insight_skills([InsightSkills.Appeal_M_Strategy] * 4),
	# # Fes3 Nozo
	# IdolUnit(728, "Fes3", limit_break = 5) \
	# 	.set_bond_board(**{ 'bond_level': 266, 'board_level': 260, 'unlocked_tiles' : True }) \
	#     .set_insight_skills([InsightSkills.Appeal_M_Strategy] * 4),
	# # Party Kotori
	# IdolUnit(514, "Party", limit_break = 5) \
	# 	.set_bond_board(**{ 'bond_level': 91,  'board_level': 60,  'unlocked_tiles' : [ BondParameter.Appeal, BondParameter.Technique, BondParameter.AttributeBonus ] }) \
	#     .set_insight_skills([InsightSkills.Appeal_M_Strategy] * 4),
	    
	# Party Maki
	IdolUnit(755, "Party", limit_break = 5) \
		.set_bond_board(**{ 'bond_level': 100, 'board_level': 60, 'unlocked_tiles' : [ BondParameter.Appeal, BondParameter.AttributeBonus ] }) \
	    .set_insight_skills([InsightSkills.Appeal_M_Attribute] * 4),
	# Lightning Nozo
	IdolUnit(839, "Lightning", limit_break = 5) \
		.set_bond_board(**{ 'bond_level': 270, 'board_level': 260, 'unlocked_tiles' : True }) \
	    .set_insight_skills([InsightSkills.Appeal_M_Strategy] * 3),
	# # Fes3 Maru
	# IdolUnit(782, "Fes3", limit_break = 5) \
	# 	.set_bond_board(**{ 'bond_level': 124, 'board_level': 120, 'unlocked_tiles' : True }) \
	#     .set_insight_skills([InsightSkills.Appeal_M_Strategy] * 4),
	# Fes2 You
	IdolUnit(393, "Fes2", limit_break = 5) \
		.set_bond_board(**{ 'bond_level': 103, 'board_level': 80,  'unlocked_tiles' : [BondParameter.CritPower] }) \
	    .set_insight_skills([InsightSkills.Appeal_M_Strategy] * 4),

	# Initial Kanan
	IdolUnit(48, "Initial", limit_break = 1) \
		.set_bond_board(**{ 'bond_level': 108, 'board_level': 60,  'unlocked_tiles'  : [] }) \
	    .set_insight_skills([InsightSkills.Appeal_M_Group] * 2),
	# Star Setsu
	IdolUnit(713, "Star", limit_break = 0) \
		.set_bond_board(**{ 'bond_level': 81,  'board_level': 40,  'unlocked_tiles' : [ BondParameter.CritRate ] }) \
	    .set_insight_skills([InsightSkills.Appeal_M_Group] * 2),
	# Party Ransu
	IdolUnit(629, "Party", limit_break = 1) \
		.set_bond_board(**{ 'bond_level': 50,  'board_level': 30,  'unlocked_tiles' : [] }) \
		.set_insight_skills([InsightSkills.Appeal_M_Group] * 4),
])

the_best_team.set_accessories({
	Strategy.Red : [
		Accessories.Belt.get(Attribute.Cool,      Rarity.UR),
		Accessories.Belt.get(Attribute.Natural,   Rarity.UR),
		Accessories.Bracelet.get(Attribute.Smile, Rarity.UR),
	],
	Strategy.Green : [
		Accessories.Brooch.get(Attribute.Smile,   Rarity.UR),
		Accessories.Bangle.get(Attribute.Pure,    Rarity.UR),
		Accessories.Bangle.get(Attribute.Active,  Rarity.UR),
	],
	Strategy.Blue : [
		Accessories.Bracelet.get(Attribute.Active, Rarity.UR),
		Accessories.Bracelet.get(Attribute.Active, Rarity.UR),
		Accessories.Bracelet.get(Attribute.Active, Rarity.UR),
	],
})

song_info = SongInfo.make_attribute_gimmick(Attribute.Smile, SkillEffectType.ReduceAppealBaseBonus, 0.25)
the_best_team.calculate_stats(song_info)

# strats = the_best_team.get_units_per_strategy()
# print(strats)
