from aenum import Enum

class dotdict(dict):
	"""dot.notation access to dictionary attributes"""
	__getattr__ = dict.get
	__setattr__ = dict.__setitem__
	__delattr__ = dict.__delitem__

class Locale(Enum):
	_init_ = 'value locale adjective suffix'
	
	JP = 1, 'Japan',  'Japanese', '_jp'
	WW = 2, 'Global', 'global',   '_ww'

class Rarity(Enum):
	_init_ = 'value max_level'
	
	R  = 10, 40
	SR = 20, 60
	UR = 30, 80

class Type(Enum):
	_init_ = 'value full_name valid'
	
	Unset = 0, "Unset",   False
	Vo    = 1, "Voltage", True
	Sp    = 2, "Special", True
	Gd    = 3, "Guard",   True
	Sk    = 4, "Skill",   True
	
	@classmethod
	def get_valid(cls):
		ret = []
		for e in cls:
			if e.valid:
				ret.append(e)
		return ret

class Attribute(Enum):
	_init_ = 'value valid'
	
	Unset     = 0, False
	Smile     = 1, True
	Pure      = 2, True
	Cool      = 3, True
	Active    = 4, True
	Natural   = 5, True
	Elegant   = 6, True
	
	@classmethod
	def get_valid(cls):
		ret = []
		for e in cls:
			if e.valid:
				ret.append(e)
		return ret

class Group(Enum):
	_init_ = 'value tag display_name'
	
	Muse        = 1, 'muse',       'µ\'s'
	Aqours      = 2, 'aqours',     'Aqours'
	Nijigasaki  = 3, 'nijigasaki', 'Nijigasaki'
#	Liella      = 4, 'liella', 'Liella'
	
class Year(Enum):
	_init_ = 'value display_name'
	
	First  = 1, '1st year'
	Second = 2, '2nd year'
	Third  = 3, '3rd year'
	
class Subunit(Enum):
	_init_ = 'value display_name'
	
	Printemps    = 1,  "Printemps"
	Lilywhite    = 2,  "lilywhite"
	Bibi         = 3,  "BiBi"
	
	Azalea       = 4,  "AZALEA"
	Cyaron       = 5,  "CYaRon!"
	Guiltykiss   = 6,  "Guilty Kiss"
	
	Quartz       = 7,  "QU4RTZ"
	Diverdiva    = 8,  "DiverDiva"
	Azuna        = 9,  "AZUNA"
	Rebirth      = 10, "R3BIRTH"
	
#	Liella       = 11, "Liella"
	
class Member(Enum):
	_init_ = 'value full_name group year subunit'
	
	# ------------ Otonokizaka / µ's ------------
	Hanayo   = 8,   "Hanayo Koizumi",     Group.Muse, Year.First, Subunit.Printemps
	Rin      = 5,   "Rin Hoshizora",      Group.Muse, Year.First, Subunit.Lilywhite
	Maki     = 6,   "Maki Nishikino",     Group.Muse, Year.First, Subunit.Bibi

	Honoka   = 1,   "Honoka Kousaka",     Group.Muse, Year.Second, Subunit.Printemps
	Kotori   = 3,   "Kotori Minami",      Group.Muse, Year.Second, Subunit.Printemps
	Umi      = 4,   "Umi Sonoda",         Group.Muse, Year.Second, Subunit.Lilywhite

	Nozomi   = 7,   "Nozomi Toujou",      Group.Muse, Year.Third, Subunit.Lilywhite
	Eli      = 2,   "Eli Ayase",          Group.Muse, Year.Third, Subunit.Bibi
	Nico     = 9,   "Nico Yazawa",        Group.Muse, Year.Third, Subunit.Bibi

	# ------------ Uranohoshi / Aqours ------------
	Hanamaru = 107, "Hanamaru Kunikida",  Group.Aqours, Year.First, Subunit.Azalea
	Yoshiko  = 106, "Yoshiko Tsushima",   Group.Aqours, Year.First, Subunit.Guiltykiss
	Ruby     = 109, "Ruby Kurosawa",      Group.Aqours, Year.First, Subunit.Cyaron

	Chika    = 101, "Chika Takami",       Group.Aqours, Year.Second, Subunit.Cyaron
	Riko     = 102, "Riko Sakurauchi",    Group.Aqours, Year.Second, Subunit.Guiltykiss
	You      = 105, "You Watanabe",       Group.Aqours, Year.Second, Subunit.Cyaron

	Kanan    = 103, "Kanan Matsuura",     Group.Aqours, Year.Third, Subunit.Azalea
	Dia      = 104, "Dia Kurosawa",       Group.Aqours, Year.Third, Subunit.Azalea
	Mari     = 108, "Mari Ohara",         Group.Aqours, Year.Third, Subunit.Guiltykiss

	# ------------ Nijigasaki ------------
	Rina     = 209, "Rina Tennouji",      Group.Nijigasaki, Year.First, Subunit.Quartz
	Kasumi   = 202, "Kasumi Nakasu",      Group.Nijigasaki, Year.First, Subunit.Quartz
	Shizuku  = 203, "Shizuku Ousaka",     Group.Nijigasaki, Year.First, Subunit.Azuna
	Shioriko = 210, "Shioriko Mifune",    Group.Nijigasaki, Year.First, Subunit.Rebirth

	Ayumu    = 201, "Ayumu Uehara",       Group.Nijigasaki, Year.Second, Subunit.Azuna
	Setsuna  = 207, "Setsuna Yuuki",      Group.Nijigasaki, Year.Second, Subunit.Azuna
	Ai       = 205, "Ai Miyashita",       Group.Nijigasaki, Year.Second, Subunit.Diverdiva
	Lanzhu   = 212, "Lanzhu Zhong",       Group.Nijigasaki, Year.Second, Subunit.Rebirth

	Emma     = 208, "Emma Verde",         Group.Nijigasaki, Year.Third, Subunit.Quartz
	Kanata   = 206, "Kanata Konoe",       Group.Nijigasaki, Year.Third, Subunit.Quartz
	Karin    = 204, "Karin Asaka",        Group.Nijigasaki, Year.Third, Subunit.Diverdiva
	Mia      = 211, "Mia Taylor",         Group.Nijigasaki, Year.Third, Subunit.Rebirth

	# ------------ Liella ------------
#	Kanon    = 301, "Kanon Shibuya",      Group.Liella, Year.Second, Subunit.Liella
#	Keke     = 302, "Keke Tang",          Group.Liella, Year.Second, Subunit.Liella
#	Chisato  = 303, "Chisato Arashi",     Group.Liella, Year.Second, Subunit.Liella
#	Sumire   = 304, "Sumire Heanna",      Group.Liella, Year.Second, Subunit.Liella
#	Ren      = 305, "Ren Hazuki",         Group.Liella, Year.Second, Subunit.Liella

#	Kinako   = 306, "Kinako Sakurakoji",  Group.Liella, Year.First, Subunit.Liella
#	Mei      = 307, "Mei Yoneme",         Group.Liella, Year.First, Subunit.Liella
#	Shiki    = 308, "Shiki Wakana",       Group.Liella, Year.First, Subunit.Liella
#	Natsumi  = 309, "Natsumi Onitsuka",   Group.Liella, Year.First, Subunit.Liella
			
	def __getattr__(self, attr):
		if attr == "first_name":
			return self.full_name.split(' ', 1)[0]
			
		if attr == "last_name": 
			return self.full_name.split(' ', 1)[1]
			
		return Enum.__getattribute__(self, attr)

class Source(Enum):
	_init_ = 'value display_name'
	
	Unspecified = 1, 'Initial'
	Event       = 2, 'Event'
	Gacha       = 3, 'Gacha'
	# 4th index is for the deprecated gacha part 2 
	Spotlight   = 5, 'Spotlight'
	Festival    = 6, 'Festival'
	Party       = 7, 'Party'
	
	@classmethod
	def get_banner_type(cls, source):
		for banner_type in BannerType:
			if banner_type.source == source:
				return banner_type
		
		return BannerType.Unset
	
	def __getattr__(self, attr):
		if attr == "banner_type":
			return Source.get_banner_type(self)
			
		return Enum.__getattribute__(self, attr)
	
	
class SkillTarget(Enum):
	Unknown       = 0
	All           = 1
	Group         = 2
	SameStrategy  = 3
	SameAttribute = 4
	SameYear      = 5
	SameSchool    = 6
	SameType      = 7
	SameMember    = 8
	SameSubunit   = 9
	Self          = 10
	
class SkillEffectType(Enum):
	AddStaminaBase   = 9
	AddAppealBase    = 10
	AddTechniqueBase = 11
	
	AddAppealBaseBonus = 26
	ReduceAppealBaseBonus = 84
	
class Ordinal(): pass
class SortingOrder(Enum):
	Ascending  = 1
	Descending = 2
	
class EventType(Enum):
	_init_ = 'value'
	
	Unset    = 0
	Story    = 1
	Exchange = 2
	
	@classmethod
	def from_string(cls, name):
		for e in cls:
			if e.name == name:
				return e
		
		return EventType.Unset
	
class BannerType(Enum):
	_init_ = 'value valid source'
	
	Unset     = 0, False, Source.Unspecified
	Spotlight = 1, True,  Source.Spotlight
	Festival  = 2, True,  Source.Festival
	Party     = 3, True,  Source.Party
	Other     = 4, False, Source.Unspecified
	Gacha     = 5, False, Source.Gacha
	
	@classmethod
	def from_string(cls, name):
		for e in cls:
			if e.name == name:
				return e
		
		return BannerType.Unset
	
	@classmethod
	def get_valid(cls):
		ret = []
		for e in cls:
			if e.valid:
				ret.append(e)
		return ret
	
class MetadataType(Enum):
	_init_ = 'value prefix category_type'
	
	Event  = 1, 'event_',  EventType
	Banner = 2, 'banner_', BannerType
