from enum import Enum
from .Enums import *

class AccessoryType(Enum):
	Brooch     = 1
	Bracelet   = 2
	Keychain   = 3
	Hairpin    = 4
	Wristband  = 5
	Towel      = 6
	Necklace   = 7
	Earring    = 1
	Ribbon     = 8
	Pouch      = 9
	
	Choker     = 10
	Bangle     = 11
	Belt       = 12
	
class AccessoryEffectType(Enum):
	Percentage = 1
	Absolute   = 2

class AccessoryBase():
	def __init__(self, rarity, values, parameters):
		if isinstance(values, tuple) and len(values) == 2:
			self.scaling_per_lb = False
			values = [values] * 6
		elif isinstance(values, list) and len(values) == 6 and isinstance(values[0], tuple):
			self.scaling_per_lb = True
		else:
			raise Exception("Accessory values must be a tuple or a list of six tuples of (min, max).")
		
		self.rarity = rarity
		
		self.values, self.value_diffs = values, [vmax - vmin for vmin, vmax in values]
		self.parameters, self.parameter_diffs = parameters, [vmax - vmin for vmin, vmax in parameters]
	
	def calculate_skill_value(self, skill_level, limit_break):
		assert limit_break >= 0 and limit_break <= 5
		assert skill_level >= 1 and skill_level <= (self.rarity.value // 2 + limit_break)
		
		max_skill_level = self.rarity.value // 2 + (limit_break if self.scaling_per_lb else 5)
		return (skill_level - 1) * (self.value_diffs[limit_break] / (max_skill_level - 1)) + self.values[limit_break][0]
	
	def calculate_parameters(self, accessory_level):
		assert accessory_level >= 1 and accessory_level <= self.rarity.value + 30
		return [round((accessory_level - 1) * (diffs / (self.rarity.value + 30 - 1)) + params[0]) for diffs, params in zip(self.parameter_diffs, self.parameters)]

class Accessory():
	LevelIncrements = [0, 5, 10, 15, 20, 30]
	
	def __init__(self, accessory_type, effect_type, attribute, rarity, accessory, limit_break, accessory_level, skill_level):
		assert limit_break >= 0 and limit_break <= 5
		
		if skill_level == None: skill_level = (rarity.value // 2 + limit_break)
		assert skill_level >= 1 and skill_level <= (rarity.value // 2 + limit_break)
		
		max_level = rarity.value + Accessory.LevelIncrements[limit_break]
		if accessory_level == None: accessory_level = max_level
		assert accessory_level >= 1 and accessory_level <= max_level
		
		self.type = accessory_type
		self.effect_type = effect_type
		self.attribute = attribute
		
		self.rarity = rarity
		self.accessory = accessory
		self.accessory_level = accessory_level
		self.limit_break = limit_break
		self.skill_level = skill_level
	
	def __str__(self):
		appeal, stamina, technique = self.get_parameters()
		s  = f"{self.type.name} ({self.rarity.name} {self.attribute.name}) (Level {self.accessory_level}/{self.get_max_accessory_level()})\n"
		s += f"  Parameters      : Appeal {appeal} / Stamina {stamina} / Technique {technique}\n"
		s += f"  Accessory Skill : {self.skill_level}/{self.get_max_skill_level()}\n"
		
		if self.effect_type == AccessoryEffectType.Percentage:
			s += f"  Skill Effect    : {self.get_skill_value():0.2f}%\n"
			
		elif self.effect_type == AccessoryEffectType.Absolute:
			s += f"  Skill Effect    : {self.get_skill_value():0.2f}\n"
			
		return s
	
	def get_max_accessory_level(self):
		return self.rarity.value + Accessory.LevelIncrements[self.limit_break]
		
	def get_max_accessory_level_by_rarity(self):
		return 30 + self.rarity.value
		
	def set_accessory_level(self, accessory_level):
		assert accessory_level >= 1 and accessory_level <= self.get_max_accessory_level()
		self.accessory_level = accessory_level
	
	def set_limit_break(self, limit_break):
		assert limit_break >= 0 and limit_break <= 5
		self.limit_break = limit_break
	
	def get_max_skill_level(self):
		return self.rarity.value // 2 + self.limit_break
	
	def set_skill_level(self, skill_level):
		assert skill_level >= 1 and skill_level <= (self.rarity.value // 2 + self.limit_break)
		self.skill_level = skill_level
	
	def get_skill_value(self):
		return self.accessory.calculate_skill_value(self.skill_level, self.limit_break)
	
	def get_parameters(self):
		return self.accessory.calculate_parameters(self.accessory_level)
	
	
class AccessoryFactory():
	def __init__(self, accessory_type, effect_type, values_per_rarity, parameters_per_rarity, rarities=list(Rarity)):
		self.type = accessory_type
		self.effect_type = effect_type
		
		self.accessories = {}
		for rarity, values, parameters in zip(rarities, values_per_rarity, parameters_per_rarity):
			self.accessories[rarity] = AccessoryBase(rarity, values, parameters)
	
	def __getitem__(self, key):
		return self.get_rarity(key)
	
	def get_rarity(self, rarity):
		return self.accessories[rarity]

	def get(self, attribute = Attribute.Unset, rarity = Rarity.UR, limit_break = 5, level = None, skill = None):
		return Accessory(self.type, self.effect_type, attribute, rarity, self.accessories[rarity], limit_break, level, skill)
		
class Accessories():
	BaselineParameters = [
		# Appeal       Stamina     Technique
		[ (129, 431),  (97, 323),  (97, 323)  ], # R parameters
		[ (192, 640),  (144, 480), (144, 480) ], # SR parameters
		[ (312, 1040), (234, 780), (234, 780) ], # UR parameters
	]
	
	Brooch     = AccessoryFactory(AccessoryType.Brooch,    AccessoryEffectType.Percentage, [(1.2, 2.5), (1.8, 3.6), (2.5, 5.0)], BaselineParameters)
	Bracelet   = AccessoryFactory(AccessoryType.Bracelet,  AccessoryEffectType.Percentage, [(1.2, 2.5), (1.8, 3.6), (2.5, 5.0)], BaselineParameters)
	
	Keychain   = AccessoryFactory(AccessoryType.Keychain,  AccessoryEffectType.Percentage, [(1.2, 2.5), (1.8, 3.6), (2.5, 5.0)], BaselineParameters)
	Hairpin    = AccessoryFactory(AccessoryType.Hairpin,   AccessoryEffectType.Percentage, [(1.2, 2.5), (1.8, 3.6), (2.5, 5.0)], BaselineParameters)
	Wristband  = AccessoryFactory(AccessoryType.Wristband, AccessoryEffectType.Percentage, [(1.2, 2.5), (1.8, 3.6), (2.5, 5.0)], BaselineParameters)
	Towel      = AccessoryFactory(AccessoryType.Towel,     AccessoryEffectType.Percentage, [(1.2, 2.5), (1.8, 3.6), (2.5, 5.0)], BaselineParameters)
	
	Necklace   = AccessoryFactory(AccessoryType.Necklace,  AccessoryEffectType.Percentage, [(0.5, 1.0), (0.7, 1.5), (1.0, 2.0)], BaselineParameters)
	Earring    = AccessoryFactory(AccessoryType.Earring,   AccessoryEffectType.Percentage, [(0.5, 1.0), (0.7, 1.5), (1.0, 2.0)], BaselineParameters)
	
	Ribbon     = AccessoryFactory(AccessoryType.Ribbon,    AccessoryEffectType.Absolute,   [(125, 250), (180, 360), (250, 500)], BaselineParameters)
	Pouch      = AccessoryFactory(AccessoryType.Pouch,     AccessoryEffectType.Absolute,   [(125, 250), (180, 360), (250, 500)], BaselineParameters)
	
	DLPParameters = [ [(233, 780), (196, 650), (352, 1170)]  ] # Only UR rarity exists for DLP accessories
	
	Choker     = AccessoryFactory(AccessoryType.Choker,    AccessoryEffectType.Percentage, [[(1.0, 4.0),  (1.0, 5.0),  (1.0, 6.0),  (1.0, 7.0),  (1.0, 8.0),  (1.0, 10.0)]], DLPParameters, [Rarity.UR])
	Bangle     = AccessoryFactory(AccessoryType.Bangle,    AccessoryEffectType.Percentage, [[(5.0, 10.0), (5.0, 12.0), (5.0, 14.0), (5.0, 16.0), (5.0, 18.0), (5.0, 20.0)]], DLPParameters, [Rarity.UR])
	Belt       = AccessoryFactory(AccessoryType.Belt,      AccessoryEffectType.Percentage, [[(1.0, 1.5),  (1.0, 2.0),  (1.0, 2.5),  (1.0, 3.0),  (1.0, 4.0),  (1.0, 5.0)]],  DLPParameters, [Rarity.UR])


## TEST CODE
if __name__ == "__main__":
	# print(Accessories.Bracelet.get(limit_break=5, skill=1))
	print(Accessories.Keychain.get(Attribute.Natural, Rarity.UR, limit_break=5, skill=10))
	
	print(Accessories.Belt.get(Attribute.Natural, Rarity.UR, limit_break=5, skill=15))
	print(Accessories.Ribbon.get(Attribute.Cool, Rarity.UR, limit_break=0, skill=15))
