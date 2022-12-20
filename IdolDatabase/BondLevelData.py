import math
import collections
from enum import Enum

if __name__ == "__main__":
	from Enums import *
else:
	from .Enums import *

class BondParameter(Enum):
	Appeal         = 1
	Stamina        = 2
	Technique      = 3

	CritRate       = 4
	CritPower      = 5

	SpGain         = 6
	SpVoltage      = 7

	VoPenalty      = 8
	SpPenalty      = 9
	GdPenalty      = 10
	SkPenalty      = 11

	AttributeBonus = 12

	URLevel        = 13
	SRLevel        = 14
	RLevel         = 15


class IdolBondBonusesValueError(Exception): pass
class IdolBondBonuses():
	BOND_PARAMETER_FIELDS = [e for e in BondParameter]
	
	BOND_BOARD_LEVELS = [
		1,   3,   5,   7,  10,  15,  20,  25,  30,  35,
		40,  50,  60,  70,  80,  90, 100, 120, 140, 160,
		180, 200, 220, 240, 260, 280, 300, 320, 340, 360,
		380, 400,
	]
	
	@staticmethod
	def get_board_index(board_level):
		try:
			return IdolBondBonuses.BOND_BOARD_LEVELS.index(board_level)
		except ValueError:
			raise IdolBondBonusesValueError(f"Bond board level '{board_level}' does not exist.")
	
	@staticmethod
	def get_max_board_level_for_bond_level(bond_level):
		for board_level in reversed(IdolBondBonuses.BOND_BOARD_LEVELS):
			if board_level <= bond_level:
				return board_level
		
		raise IdolBondBonusesValueError(f"Invalid bond level.")
	
	@staticmethod
	def get_parameter_bonus(bond_level : int):
		# https://suyo.be/sifas/wiki/gameplay/bond-level
		# https://suyo.be/sifas/wiki/calculations/bond-level
		bonus = max(0, (5 * bond_level - 9)) ** 0.35
		return round(bonus, 2)
		
	# --------------------------------------------------
	
	# Bond board tiles and completion bonuses seem to loop every 10 boards
	
	BOND_BOARD_TILES = [
		{  BondParameter.Appeal : 0.1,  BondParameter.Stamina : 0.1,  BondParameter.Technique : 0.1,  BondParameter.CritRate  : 0.5,  BondParameter.SpGain         : 0.5, },
		{  BondParameter.Appeal : 0.1,  BondParameter.Stamina : 0.1,  BondParameter.Technique : 0.1,  BondParameter.CritPower : 5.0,  BondParameter.RLevel         : 6,   },
		{  BondParameter.Appeal : 0.1,  BondParameter.Stamina : 0.1,  BondParameter.Technique : 0.1,  BondParameter.SpVoltage : 0.2,  BondParameter.AttributeBonus : 2.5, },
		{  BondParameter.Appeal : 0.1,  BondParameter.Stamina : 0.1,  BondParameter.Technique : 0.1,  BondParameter.GdPenalty : 0.5,  BondParameter.SRLevel        : 4  , },
		{  BondParameter.Appeal : 0.1,  BondParameter.Stamina : 0.1,  BondParameter.Technique : 0.1,  BondParameter.CritPower : 5.0,  BondParameter.SpVoltage      : 0.2, },
		{  BondParameter.Appeal : 0.1,  BondParameter.Stamina : 0.1,  BondParameter.Technique : 0.1,  BondParameter.SkPenalty : 0.5,  BondParameter.SpGain         : 0.5, },
		{  BondParameter.Appeal : 0.1,  BondParameter.Stamina : 0.1,  BondParameter.Technique : 0.1,  BondParameter.CritRate  : 0.5,  BondParameter.URLevel        : 2,   },
		{  BondParameter.Appeal : 0.1,  BondParameter.Stamina : 0.1,  BondParameter.Technique : 0.1,  BondParameter.SpPenalty : 0.5,  BondParameter.SpGain         : 0.5, },
		{  BondParameter.Appeal : 0.1,  BondParameter.Stamina : 0.1,  BondParameter.Technique : 0.1,  BondParameter.VoPenalty : 0.5,  BondParameter.CritRate       : 0.5, },
		{  BondParameter.Appeal : 0.1,  BondParameter.Stamina : 0.1,  BondParameter.Technique : 0.1,  BondParameter.CritPower : 5.0,  BondParameter.SpVoltage      : 0.2, },
	]
	
	BOND_BOARD_COMPLETION_BONUS = [
		# Appeal  Stamina  Technique  Crit Rate  Crit Power  Sp Gain  Sp Voltage  Vo Penalty  Sp Penalty  Gd Penalty  Sk Penalty  Attribute Bonus  UR Level  SR Level  R Level
		( 1.0,    0.0,     0.0,       0.0,       0.0,        0.0,     0.0,        0.0,        0.0,        0.0,        0.0,        0.0,             0,        0,        0,      ),
		( 0.0,    1.0,     0.0,       0.0,       0.0,        0.0,     0.0,        0.0,        0.0,        0.0,        0.0,        0.0,             0,        0,        0,      ),
		( 0.0,    0.0,     1.0,       0.0,       0.0,        0.0,     0.0,        0.0,        0.0,        0.0,        0.0,        0.0,             0,        0,        0,      ),
		( 0.0,    0.0,     0.0,       0.0,       0.0,        0.0,     1.0,        0.0,        0.0,        0.0,        0.0,        0.0,             0,        0,        0,      ),
		( 0.0,    0.0,     0.0,       0.0,       0.0,        2.0,     0.0,        0.0,        0.0,        0.0,        0.0,        0.0,             0,        0,        0,      ),
		( 0.0,    0.0,     0.0,       1.0,       0.0,        0.0,     0.0,        0.0,        0.0,        0.0,        0.0,        0.0,             0,        0,        0,      ),
		( 0.0,    0.0,     0.0,       0.0,       20.0,       0.0,     0.0,        0.0,        0.0,        0.0,        0.0,        0.0,             0,        0,        0,      ),
		( 0.0,    0.0,     0.0,       0.0,       0.0,        0.0,     0.0,        0.0,        0.0,        0.0,        0.0,        5.0,             0,        0,        0,      ),
		( 0.0,    0.0,     0.0,       0.0,       0.0,        0.0,     1.0,        0.0,        0.0,        0.0,        0.0,        0.0,             0,        0,        0,      ),
		( 0.0,    0.0,     0.0,       0.0,       0.0,        0.0,     0.0,        0.0,        0.0,        0.0,        0.0,        0.0,             2,        4,        6,      ),
	]
		
	# --------------------------------------------------
	
	@staticmethod
	def get_board_completion_bonus(board_level : int):
		board_index = IdolBondBonuses.get_board_index(board_level)
		return IdolBondBonuses.BOND_BOARD_COMPLETION_BONUS[board_index % len(IdolBondBonuses.BOND_BOARD_COMPLETION_BONUS)]
		
	@staticmethod
	def get_cumulative_completion_parameters(start_board_level : int = 1, end_board_level : int = None, end_inclusive : bool = True):
		parameters = [0] * len(IdolBondBonuses.BOND_PARAMETER_FIELDS)
		for board_level, bonuses in IdolBondBonuses.board_completion_bonuses(start_board_level, end_board_level, end_inclusive):
			parameters = [sum(x) for x in zip(parameters, bonuses)]
		parameters = dict(zip(IdolBondBonuses.BOND_PARAMETER_FIELDS, parameters))
		return parameters
		
	@staticmethod
	def board_completion_bonuses(start_board_level : int = 1, end_board_level : int = None, end_inclusive : bool = True):
		for index, board_level in enumerate(IdolBondBonuses.BOND_BOARD_LEVELS):
			if board_level < start_board_level:
				continue
			if isinstance(end_board_level, int):
				if end_inclusive     and board_level >  end_board_level: break
				if not end_inclusive and board_level >= end_board_level: break
			yield (board_level, IdolBondBonuses.BOND_BOARD_COMPLETION_BONUS[index % len(IdolBondBonuses.BOND_BOARD_COMPLETION_BONUS)])
		
	# --------------------------------------------------
	
	@staticmethod
	def get_board_tiles(board_level : int):
		board_index = IdolBondBonuses.get_board_index(board_level)
		return IdolBondBonuses.BOND_BOARD_TILES[board_index % len(IdolBondBonuses.BOND_BOARD_TILES)]
	
	@staticmethod
	def board_tiles(start_board_level : int = 1, end_board_level : int = None, end_inclusive : bool = True):
		for index, board_level in enumerate(IdolBondBonuses.BOND_BOARD_LEVELS):
			if board_level < start_board_level:
				continue
			if isinstance(end_board_level, int):
				if end_inclusive     and board_level >  end_board_level: break
				if not end_inclusive and board_level >= end_board_level: break
				
			yield (board_level, IdolBondBonuses.BOND_BOARD_TILES[index % len(IdolBondBonuses.BOND_BOARD_TILES)])
	
	@staticmethod
	def get_cumulative_tile_parameters(start_board_level : int = 1, end_board_level : int = None, end_inclusive : bool = True):
		parameters = dict.fromkeys(IdolBondBonuses.BOND_PARAMETER_FIELDS, 0)
		for board_level, board_tiles in IdolBondBonuses.board_tiles(start_board_level, end_board_level, end_inclusive):
			for tile_parameter, value in board_tiles.items():
				parameters[tile_parameter] += value
		return parameters
		
	# --------------------------------------------------
	
	@staticmethod
	def get_board_parameters(bond_level : int, board_level : int, unlocked_tiles : list):
		"""Return total cumulative bond board parameters for the given bond level, board level and unlocked tiles.
		
		Arguments:
	      bond_level     : integer value for bond level. Min value 1.
	      
	      board_level    : integer value for board level. Min value 1, max value [bond_level].
	                     :  Value must exist in BOND_BOARD_LEVELS list.
	                     
	      unlocked_tiles : Can be a boolean or a list.
	                     :   If boolean:  True  = all tiles of current board are unlocked
	                     :                False = no tiles of current board are unlocked (the same as supplying an empty list)
	                     :   If list:     The list should contain up to 5 values of enum type BondParameter
	                     :                and the values must exist in the list returned by method get_board_tiles(board_level).
		"""
		
		if bond_level < 1:
			raise IdolBondBonusesValueError(f"Invalid bond level.")
			
		if board_level not in IdolBondBonuses.BOND_BOARD_LEVELS:
			raise IdolBondBonusesValueError(f"Given board level ({board_level}) is not a valid board level.")
		
		max_board_level = IdolBondBonuses.get_max_board_level_for_bond_level(bond_level)
		if board_level > max_board_level:
			raise IdolBondBonusesValueError(f"Bond level ({bond_level}) is lower than required for the board level ({max_board_level}).")
		
		current_tiles = IdolBondBonuses.get_board_tiles(board_level)
		
		if isinstance(unlocked_tiles, bool):
			current_board_completed = (unlocked_tiles == True)
			
		elif isinstance(unlocked_tiles, list):
			assert(len(unlocked_tiles) <= 5)
			current_board_completed = len(unlocked_tiles) == 5 and collections.Counter(unlocked_tiles) == collections.Counter(current_tiles.keys())
		
		else:
			raise IdolBondBonusesValueError("Argument 'unlocked_tiles' should be a boolean or a list of BondParameter enum values.")
		
		sum_dicts = lambda a, b: {k: a.get(k, 0) + b.get(k, 0) for k in a.keys()}
		parameters = sum_dicts(
			IdolBondBonuses.get_cumulative_completion_parameters(end_board_level=board_level, end_inclusive=current_board_completed),
			IdolBondBonuses.get_cumulative_tile_parameters(end_board_level=board_level, end_inclusive=current_board_completed)
		)

		if not current_board_completed and isinstance(unlocked_tiles, list):
			for tile_parameter in unlocked_tiles:
				if tile_parameter not in current_tiles:
					raise IdolBondBonusesValueError(f"Given tile '{key}' does not exist in current board (level {board_level})")
				parameters[tile_parameter] += current_tiles[tile_parameter]

		parameter_bonus = IdolBondBonuses.get_parameter_bonus(bond_level)
		parameters[BondParameter.Appeal]    += parameter_bonus
		parameters[BondParameter.Stamina]   += parameter_bonus
		parameters[BondParameter.Technique] += parameter_bonus

		parameters[BondParameter.URLevel] += Rarity.UR.max_level
		parameters[BondParameter.SRLevel] += Rarity.SR.max_level
		parameters[BondParameter.RLevel]  += Rarity.R.max_level

		if __name__ == "__main__":
			print()
			for k, v in parameters.items():
				print(f"   {k.name:<15}  : {v:>4.2f}")
			print()
		
		return parameters


## TEST CODE
if __name__ == "__main__":
	# max_board_level = IdolBondBonuses.get_max_board_level_for_bond_level(bond_level=260)
	# print("max_board_level", max_board_level)
	
	# board_index = IdolBondBonuses.get_board_index(max_board_level)
	# print("board_index", board_index)
	
	# completion = IdolBondBonuses.get_board_completion_bonus(max_board_level)
	# print(completion)
	
	# for board_level, completion in IdolBondBonuses.board_completion_bonuses(end_board_level=260, end_inclusive = False):
	# 	print(board_level, completion)
	
	# IdolBondBonuses.get_board_parameters(bond_level=261, board_level=260, unlocked_tiles=True)
	IdolBondBonuses.get_board_parameters(bond_level=92, board_level=60, unlocked_tiles=[BondParameter.AttributeBonus])
	
	# IdolBondBonuses.get_board_parameters(103, 50, [ BondParameter.Appeal, BondParameter.CritPower ])
	# IdolBondBonuses.get_board_parameters(102, 40, [ BondParameter.Appeal, BondParameter.CritRate ])
	# IdolBondBonuses.get_board_parameters(77, 30, [ BondParameter.CritRate ])
