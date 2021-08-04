import math
from enum import Enum

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
	
	BOND_LEVEL_PARAMETER_BONUS = dict([
		(  1,  0.00),  (  2,  1.00),  (  3,  1.87),  (  4,  2.31),  (  5,  2.64),  
		(  6,  2.90),  (  7,  3.13),  (  8,  3.33),  (  9,  3.51),  ( 10,  3.67),  
		( 11,  3.82),  ( 12,  3.96),  ( 13,  4.09),  ( 14,  4.22),  ( 15,  4.33),  
		( 16,  4.45),  ( 17,  4.55),  ( 18,  4.66),  ( 19,  4.75),  ( 20,  4.85),  
		( 21,  4.94),  ( 22,  5.03),  ( 23,  5.12),  ( 24,  5.20),  ( 25,  5.28),  
		( 26,  5.36),  ( 27,  5.43),  ( 28,  5.51),  ( 29,  5.58),  ( 30,  5.65),  
		( 31,  5.72),  ( 32,  5.79),  ( 33,  5.86),  ( 34,  5.92),  ( 35,  5.98),  
		( 36,  6.05),  ( 37,  6.11),  ( 38,  6.17),  ( 39,  6.23),  ( 40,  6.29),  
		( 41,  6.34),  ( 42,  6.40),  ( 43,  6.45),  ( 44,  6.51),  ( 45,  6.56),  
		( 46,  6.62),  ( 47,  6.67),  ( 48,  6.72),  ( 49,  6.77),  ( 50,  6.82),  
		( 51,  6.87),  ( 52,  6.92),  ( 53,  6.96),  ( 54,  7.01),  ( 55,  7.06),  
		( 56,  7.10),  ( 57,  7.15),  ( 58,  7.20),  ( 59,  7.24),  ( 60,  7.28),  
		( 61,  7.33),  ( 62,  7.37),  ( 63,  7.41),  ( 64,  7.46),  ( 65,  7.50),  
		( 66,  7.54),  ( 67,  7.58),  ( 68,  7.62),  ( 69,  7.66),  ( 70,  7.70),  
		( 71,  7.74),  ( 72,  7.78),  ( 73,  7.82),  ( 74,  7.85),  ( 75,  7.89),  
		( 76,  7.93),  ( 77,  7.97),  ( 78,  8.00),  ( 79,  8.04),  ( 80,  8.08),  
		( 81,  8.11),  ( 82,  8.15),  ( 83,  8.18),  ( 84,  8.22),  ( 85,  8.25),  
		( 86,  8.29),  ( 87,  8.32),  ( 88,  8.36),  ( 89,  8.39),  ( 90,  8.42),  
		( 91,  8.46),  ( 92,  8.49),  ( 93,  8.52),  ( 94,  8.56),  ( 95,  8.59),  
		( 96,  8.62),  ( 97,  8.65),  ( 98,  8.68),  ( 99,  8.72),  (100,  8.75),  
		(101,  8.78),  (102,  8.81),  (103,  8.84),  (104,  8.87),  (105,  8.90),  
		(106,  8.93),  (107,  8.96),  (108,  8.99),  (109,  9.02),  (110,  9.05),  
		(111,  9.08),  (112,  9.11),  (113,  9.14),  (114,  9.17),  (115,  9.19),  
		(116,  9.22),  (117,  9.25),  (118,  9.28),  (119,  9.31),  (120,  9.33),  
		(121,  9.36),  (122,  9.39),  (123,  9.42),  (124,  9.44),  (125,  9.47),  
		(126,  9.50),  (127,  9.52),  (128,  9.55),  (129,  9.58),  (130,  9.60),  
		(131,  9.63),  (132,  9.66),  (133,  9.68),  (134,  9.71),  (135,  9.73),  
		(136,  9.76),  (137,  9.78),  (138,  9.81),  (139,  9.83),  (140,  9.86),  
		(141,  9.88),  (142,  9.91),  (143,  9.93),  (144,  9.96),  (145,  9.98),  
		(146, 10.01),  (147, 10.03),  (148, 10.05),  (149, 10.08),  (150, 10.10),  
		(151, 10.13),  (152, 10.15),  (153, 10.17),  (154, 10.20),  (155, 10.22),  
		(156, 10.24),  (157, 10.27),  (158, 10.29),  (159, 10.31),  (160, 10.34),  
		(161, 10.36),  (162, 10.38),  (163, 10.40),  (164, 10.43),  (165, 10.45),  
		(166, 10.47),  (167, 10.49),  (168, 10.52),  (169, 10.54),  (170, 10.56),  
		(171, 10.58),  (172, 10.60),  (173, 10.63),  
	])

	BOND_BOARD_COMPLETION_BONUS = dict([
		# Board  Appeal  Stamina  Technique  Crit Rate  Crit Power  Sp Gain  Sp Voltage  Vo Penalty  Sp Penalty  Gd Penalty  Sk Penalty  Attribute Bonus  UR Level  SR Level  R Level 
		( 1,     (1.0,   0.0,     0.0,       0.0,       0.0,        0.0,     0.0,        0.0,        0.0,        0.0,        0.0,        0.0,             0,        0,        0,      ) ),
		( 3,     (0.0,   1.0,     0.0,       0.0,       0.0,        0.0,     0.0,        0.0,        0.0,        0.0,        0.0,        0.0,             0,        0,        0,      ) ),
		( 5,     (0.0,   0.0,     1.0,       0.0,       0.0,        0.0,     0.0,        0.0,        0.0,        0.0,        0.0,        0.0,             0,        0,        0,      ) ),
		( 7,     (0.0,   0.0,     0.0,       0.0,       0.0,        0.0,     1.0,        0.0,        0.0,        0.0,        0.0,        0.0,             0,        0,        0,      ) ),
		( 10,    (0.0,   0.0,     0.0,       0.0,       0.0,        2.0,     0.0,        0.0,        0.0,        0.0,        0.0,        0.0,             0,        0,        0,      ) ),
		( 15,    (0.0,   0.0,     0.0,       1.0,       0.0,        0.0,     0.0,        0.0,        0.0,        0.0,        0.0,        0.0,             0,        0,        0,      ) ),
		( 20,    (0.0,   0.0,     0.0,       0.0,       20.0,       0.0,     0.0,        0.0,        0.0,        0.0,        0.0,        0.0,             0,        0,        0,      ) ),
		( 25,    (0.0,   0.0,     0.0,       0.0,       0.0,        0.0,     0.0,        0.0,        0.0,        0.0,        0.0,        5.0,             0,        0,        0,      ) ),
		( 30,    (0.0,   0.0,     0.0,       0.0,       0.0,        0.0,     1.0,        0.0,        0.0,        0.0,        0.0,        0.0,             0,        0,        0,      ) ),
		( 35,    (0.0,   0.0,     0.0,       0.0,       0.0,        0.0,     0.0,        0.0,        0.0,        0.0,        0.0,        0.0,             2,        4,        6,      ) ),
		
		( 40,    (1.0,   0.0,     0.0,       0.0,       0.0,        0.0,     0.0,        0.0,        0.0,        0.0,        0.0,        0.0,             0,        0,        0,      ) ),
		( 50,    (0.0,   1.0,     0.0,       0.0,       0.0,        0.0,     0.0,        0.0,        0.0,        0.0,        0.0,        0.0,             0,        0,        0,      ) ),
		( 60,    (0.0,   0.0,     1.0,       0.0,       0.0,        0.0,     0.0,        0.0,        0.0,        0.0,        0.0,        0.0,             0,        0,        0,      ) ),
		( 70,    (0.0,   0.0,     0.0,       0.0,       0.0,        0.0,     1.0,        0.0,        0.0,        0.0,        0.0,        0.0,             0,        0,        0,      ) ),
		( 80,    (0.0,   0.0,     0.0,       0.0,       0.0,        2.0,     0.0,        0.0,        0.0,        0.0,        0.0,        0.0,             0,        0,        0,      ) ),
		( 90,    (0.0,   0.0,     0.0,       1.0,       0.0,        0.0,     0.0,        0.0,        0.0,        0.0,        0.0,        0.0,             0,        0,        0,      ) ),
		( 100,   (0.0,   0.0,     0.0,       0.0,       20.0,       0.0,     0.0,        0.0,        0.0,        0.0,        0.0,        0.0,             0,        0,        0,      ) ),
		( 120,   (0.0,   0.0,     0.0,       0.0,       0.0,        0.0,     0.0,        0.0,        0.0,        0.0,        0.0,        5.0,             0,        0,        0,      ) ),
		( 140,   (0.0,   0.0,     0.0,       0.0,       0.0,        0.0,     1.0,        0.0,        0.0,        0.0,        0.0,        0.0,             0,        0,        0,      ) ),
		( 160,   (0.0,   0.0,     0.0,       0.0,       0.0,        0.0,     0.0,        0.0,        0.0,        0.0,        0.0,        0.0,             2,        4,        6,      ) ),
		
		( 180,   (1.0,   0.0,     0.0,       0.0,       0.0,        0.0,     0.0,        0.0,        0.0,        0.0,        0.0,        0.0,             0,        0,        0,      ) ),
		( 200,   (0.0,   1.0,     0.0,       0.0,       0.0,        0.0,     0.0,        0.0,        0.0,        0.0,        0.0,        0.0,             0,        0,        0,      ) ),
	])

	BOND_BOARD_TILES = dict([
		( 1,   {  BondParameter.Appeal : 0.1,  BondParameter.Stamina : 0.1,  BondParameter.Technique : 0.1,  BondParameter.CritRate  : 0.5,  BondParameter.SpGain         : 0.5, } ),
		( 3,   {  BondParameter.Appeal : 0.1,  BondParameter.Stamina : 0.1,  BondParameter.Technique : 0.1,  BondParameter.CritPower : 5.0,  BondParameter.RLevel         : 6,   } ),
		( 5,   {  BondParameter.Appeal : 0.1,  BondParameter.Stamina : 0.1,  BondParameter.Technique : 0.1,  BondParameter.SpVoltage : 0.2,  BondParameter.AttributeBonus : 2.5, } ),
		( 7,   {  BondParameter.Appeal : 0.1,  BondParameter.Stamina : 0.1,  BondParameter.Technique : 0.1,  BondParameter.GdPenalty : 0.5,  BondParameter.SRLevel        : 4  , } ),
		( 10,  {  BondParameter.Appeal : 0.1,  BondParameter.Stamina : 0.1,  BondParameter.Technique : 0.1,  BondParameter.CritPower : 5.0,  BondParameter.SpVoltage      : 0.2, } ),
		( 15,  {  BondParameter.Appeal : 0.1,  BondParameter.Stamina : 0.1,  BondParameter.Technique : 0.1,  BondParameter.SkPenalty : 0.5,  BondParameter.SpGain         : 0.5, } ),
		( 20,  {  BondParameter.Appeal : 0.1,  BondParameter.Stamina : 0.1,  BondParameter.Technique : 0.1,  BondParameter.CritRate  : 0.5,  BondParameter.URLevel        : 2,   } ),
		( 25,  {  BondParameter.Appeal : 0.1,  BondParameter.Stamina : 0.1,  BondParameter.Technique : 0.1,  BondParameter.SpPenalty : 0.5,  BondParameter.SpGain         : 0.5, } ),
		( 30,  {  BondParameter.Appeal : 0.1,  BondParameter.Stamina : 0.1,  BondParameter.Technique : 0.1,  BondParameter.VoPenalty : 0.5,  BondParameter.CritRate       : 0.5, } ),
		( 35,  {  BondParameter.Appeal : 0.1,  BondParameter.Stamina : 0.1,  BondParameter.Technique : 0.1,  BondParameter.CritPower : 5.0,  BondParameter.SpVoltage      : 0.2, } ),
		
		( 40,  {  BondParameter.Appeal : 0.1,  BondParameter.Stamina : 0.1,  BondParameter.Technique : 0.1,  BondParameter.CritRate  : 0.5,  BondParameter.SpGain         : 0.5, } ),
		( 50,  {  BondParameter.Appeal : 0.1,  BondParameter.Stamina : 0.1,  BondParameter.Technique : 0.1,  BondParameter.CritPower : 5.0,  BondParameter.RLevel         : 6,   } ),
		( 60,  {  BondParameter.Appeal : 0.1,  BondParameter.Stamina : 0.1,  BondParameter.Technique : 0.1,  BondParameter.SpVoltage : 0.2,  BondParameter.AttributeBonus : 2.5, } ),
		( 70,  {  BondParameter.Appeal : 0.1,  BondParameter.Stamina : 0.1,  BondParameter.Technique : 0.1,  BondParameter.GdPenalty : 0.5,  BondParameter.SRLevel        : 4  , } ),
		( 80,  {  BondParameter.Appeal : 0.1,  BondParameter.Stamina : 0.1,  BondParameter.Technique : 0.1,  BondParameter.CritPower : 5.0,  BondParameter.SpVoltage      : 0.5, } ),
		( 90,  {  BondParameter.Appeal : 0.1,  BondParameter.Stamina : 0.1,  BondParameter.Technique : 0.1,  BondParameter.SkPenalty : 0.5,  BondParameter.SpGain         : 0.2, } ),
		( 100, {  BondParameter.Appeal : 0.1,  BondParameter.Stamina : 0.1,  BondParameter.Technique : 0.1,  BondParameter.CritRate  : 0.5,  BondParameter.URLevel        : 2,   } ),
		( 120, {  BondParameter.Appeal : 0.1,  BondParameter.Stamina : 0.1,  BondParameter.Technique : 0.1,  BondParameter.SpPenalty : 0.5,  BondParameter.SpGain         : 0.5, } ),
		( 140, {  BondParameter.Appeal : 0.1,  BondParameter.Stamina : 0.1,  BondParameter.Technique : 0.1,  BondParameter.VoPenalty : 0.5,  BondParameter.CritRate       : 0.5, } ),
		( 160, {  BondParameter.Appeal : 0.1,  BondParameter.Stamina : 0.1,  BondParameter.Technique : 0.1,  BondParameter.CritPower : 5.0,  BondParameter.SpVoltage      : 0.2, } ),
		
		( 180, {  BondParameter.Appeal : 0.1,  BondParameter.Stamina : 0.1,  BondParameter.Technique : 0.1,  BondParameter.CritRate  : 0.5,  BondParameter.SpGain         : 0.5, } ),
		( 200, {  BondParameter.Appeal : 0.1,  BondParameter.Stamina : 0.1,  BondParameter.Technique : 0.1,  BondParameter.CritPower : 5.0,  BondParameter.RLevel         : 6,   } ),
	])

	@staticmethod
	def add_parameters(a, b):
		for k in a:
			a[k] += b[k]
		return a
	
	@staticmethod
	def get_bond_parameters(bond_level, active_board_level, current_board_unlocks):
		# result = dict.fromkeys(BOND_PARAMETER_FIELDS, 0)
		result = [0] * len(IdolBondBonuses.BOND_PARAMETER_FIELDS)
		
		for level, params in IdolBondBonuses.BOND_BOARD_COMPLETION_BONUS.items():
			if level == active_board_level: break
			result = [sum(x) for x in zip(result, params)]
		
		result = dict(zip(IdolBondBonuses.BOND_PARAMETER_FIELDS, result))
		
		for level, params in IdolBondBonuses.BOND_BOARD_TILES.items():
			if level == active_board_level: break
			for key, value in params.items():
				result[key] += value
		
		current_tiles = IdolBondBonuses.BOND_BOARD_TILES[active_board_level]
		for key in current_board_unlocks:
			if key not in current_tiles:
				raise IdolBondBonusesValueError(f"Given tile '{key}' does not exist in current board (level {active_board_level})")
			result[key] += current_tiles[key]
		
		if bond_level not in IdolBondBonuses.BOND_LEVEL_PARAMETER_BONUS:
			raise IdolBondBonusesValueError("Bond bonus percentage not found in the parameter bonus list (may be unimplemented).")
		
		bonus_percentage = IdolBondBonuses.BOND_LEVEL_PARAMETER_BONUS[bond_level]
		
		result[BondParameter.Appeal]    += bonus_percentage
		result[BondParameter.Stamina]   += bonus_percentage
		result[BondParameter.Technique] += bonus_percentage
		
		result[BondParameter.URLevel] += 80
		result[BondParameter.SRLevel] += 60
		result[BondParameter.RLevel]  += 40
		
		print()
		for k, v in result.items():
			print(f"   {k.name:<15}  : {v:>4.2f}")
		print()

# IdolBondBonuses.get_bond_parameters(103, 50, [ BondParameter.Appeal, BondParameter.CritPower ])
IdolBondBonuses.get_bond_parameters(103, 50, [ BondParameter.RLevel ])
# IdolBondBonuses.get_bond_parameters(102, 40, [ BondParameter.Appeal, BondParameter.CritRate ])
# IdolBondBonuses.get_bond_parameters(77, 30, [ BondParameter.CritRate ])
