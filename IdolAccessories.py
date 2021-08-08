from IdolEnums import *

class AccessoryBase():
	def __init__(self, values, parameters):
		if isinstance(values, tuple) and len(values) == 2:
			self.scaling_per_lb = False
			values = [values] * 6
		elif isinstance(values, list) and len(values) == 6 and isinstance(values[0], tuple):
			self.scaling_per_lb = True
		else:
			raise Exception("Accessory values must be a tuple or a list of six tuples of (min, max).")
		
		self.values = values
		self.value_diffs = [b - a for a, b in self.values]
		
		self.parameters = parameters
		self.parameter_diffs = [b - a for a, b in self.parameters]
	
	def calculate_skill_value(self, skill_level, limit_break):
		assert limit_break >= 0 and limit_break <= 5
		assert skill_level >= 1 and skill_level <= (15 + limit_break)
		
		if self.scaling_per_lb:
			max_level = 15 + limit_break
		else:
			max_level = 20
		return (skill_level - 1) * (self.value_diffs[limit_break] / (max_level - 1)) + self.values[limit_break][0]
	
	def calculate_parameters(self, accessory_level):
		assert accessory_level >= 1 and accessory_level <= 60
		return [int((accessory_level - 1) * (diffs / 59) + params[0]) for diffs, params in zip(self.parameter_diffs, self.parameters)]


class Accessory():
	LevelIncrements = [0, 5, 10, 15, 20, 30]
	
	def __init__(self, name, attribute, rarity, accessory, limit_break, accessory_level, skill_level):
		assert limit_break >= 0 and limit_break <= 5
		
		if skill_level == None: skill_level = (15 + limit_break)
		assert skill_level >= 1 and skill_level <= (15 + limit_break)
		
		max_level = rarity.value + Accessory.LevelIncrements[limit_break]
		if accessory_level == None: accessory_level = max_level
		assert accessory_level >= 1 and accessory_level <= max_level
		
		self.name = name
		self.attribute = attribute
		
		self.rarity = rarity
		self.accessory = accessory
		self.accessory_level = accessory_level
		self.limit_break = limit_break
		self.skill_level = skill_level
	
	def __str__(self):
		appeal, stamina, technique = self.get_parameters()
		s  = f"{self.name} ({self.rarity.name} {self.attribute.name}) (Level {self.accessory_level}/{self.get_max_accessory_level()})\n"
		s += f"  Parameters      : Appeal {appeal} / Stamina {stamina} / Technique {technique}\n"
		s += f"  Accessory Skill : {self.skill_level}/{self.get_max_skill_level()}\n"
		s += f"  Skill Effect    : {self.get_skill_value():0.1f}%\n"
		return s
	
	def get_max_accessory_level(self):
		return self.rarity.value + Accessory.LevelIncrements[self.limit_break]
		
	def set_accessory_level(self, accessory_level):
		assert accessory_level >= 1 and accessory_level <= self.get_max_accessory_level()
		self.accessory_level = accessory_level
	
	def set_limit_break(self, limit_break):
		assert limit_break >= 0 and limit_break <= 5
		self.limit_break = limit_break
	
	def get_max_skill_level(self):
		return 15 + self.limit_break
	
	def set_skill_level(self, skill_level):
		assert skill_level >= 1 and skill_level <= (15 + self.limit_break)
		self.skill_level = skill_level
	
	def get_skill_value(self):
		return self.accessory.calculate_skill_value(self.skill_level, self.limit_break)
	
	def get_parameters(self):
		return self.accessory.calculate_parameters(self.accessory_level)
	
	
class AccessoryFactory():
	def __init__(self, name, values_per_rarity, parameters_per_rarity, rarities=list(Rarity)):
		self.name = name
		self.accessories = {}
		for rarity, values, parameters in zip(rarities, values_per_rarity, parameters_per_rarity):
			self.accessories[rarity] = AccessoryBase(values, parameters)
	
	def __getitem__(self, key):
		return self.get_rarity(key)
	
	def get_rarity(self, rarity):
		return self.accessories[rarity]

	def get(self, attribute = Attribute.Unset, rarity = Rarity.UR, limit_break = 5, level = None, skill = None):
		return Accessory(self.name, attribute, rarity, self.accessories[rarity], limit_break, level, skill)
		

class Accessories():
	BaselineParameters = [
		[(129, 431),  (97, 323),  (97, 323) ], # R parameters
		[(192, 640),  (144, 480), (144, 480)], # SR parameters
		[(312, 1040), (234, 780), (234, 780)], # UR parameters
	]
	
	Brooch     = AccessoryFactory("Brooch",    [(1.0, 2.5), (1.8, 3.6), (2.5, 5.0)], BaselineParameters)
	Bracelet   = AccessoryFactory("Bracelet",  [(1.0, 2.5), (1.8, 3.6), (2.5, 5.0)], BaselineParameters)
	
	Keychain   = AccessoryFactory("Keychain",  [(1.0, 2.5), (1.8, 3.6), (2.5, 5.0)], BaselineParameters)
	Hairpin    = AccessoryFactory("Hairpin",   [(1.0, 2.5), (1.8, 3.6), (2.5, 5.0)], BaselineParameters)
	Wristband  = AccessoryFactory("Wristband", [(1.0, 2.5), (1.8, 3.6), (2.5, 5.0)], BaselineParameters)
	Towel      = AccessoryFactory("Towel",     [(1.0, 2.5), (1.8, 3.6), (2.5, 5.0)], BaselineParameters)
	
	Necklace   = AccessoryFactory("Necklace",  [(0.5, 1.0), (0.7, 1.5), (1.0, 2.0)], BaselineParameters)
	Earring    = AccessoryFactory("Earring",   [(0.5, 1.0), (0.7, 1.5), (1.0, 2.0)], BaselineParameters)
	
	Ribbon     = AccessoryFactory("Ribbon",    [(125, 250), (180, 360), (250, 500)], BaselineParameters)
	Pouch      = AccessoryFactory("Pouch",     [(125, 250), (180, 360), (250, 500)], BaselineParameters)
	
	DLPParameters = [ [(233, 780), (196, 650), (352, 1170)]  ] # Only UR rarity exists for DLP accessories
	
	Choker     = AccessoryFactory("Choker",    [[(1.0, 4.0),  (1.0, 5.0),  (1.0, 6.0),  (1.0, 7.0),  (1.0, 8.0),  (1.0, 10.0)]], DLPParameters, [Rarity.UR])
	Bangle     = AccessoryFactory("Bangle",    [[(5.0, 10.0), (5.0, 12.0), (5.0, 14.0), (5.0, 16.0), (5.0, 18.0), (5.0, 20.0)]], DLPParameters, [Rarity.UR])
	Belt       = AccessoryFactory("Belt",      [[(1.0, 1.5),  (1.0, 2.0),  (1.0, 2.5),  (1.0, 3.0),  (1.0, 4.0),  (1.0, 5.0)]],  DLPParameters, [Rarity.UR])

print(Accessories.Brooch.get(Attribute.Smile, Rarity.UR, limit_break=5, level=60, skill=20))
print(Accessories.Necklace.get(Attribute.Natural, Rarity.UR, limit_break=3, skill=15))
print(Accessories.Choker.get(Attribute.Elegant, Rarity.UR, limit_break=1, skill=12))
