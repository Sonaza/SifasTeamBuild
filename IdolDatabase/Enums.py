from aenum import Enum
from collections import namedtuple

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
	
	# LiellaUnitA  = 11, "Liella"
	# LiellaUnitB  = 12, "Liella"
	# LiellaUnitC  = 13, "Liella"

Birthday = namedtuple('Birthday', 'month day')

class Member(Enum):
	_init_ = 'value full_name birthday group year subunit'
	
	# ------------ Otonokizaka / µ's ------------
	Hanayo   = 8,   "Hanayo Koizumi",     Birthday( 1, 17),  Group.Muse, Year.First, Subunit.Printemps
	Rin      = 5,   "Rin Hoshizora",      Birthday(11,  1),  Group.Muse, Year.First, Subunit.Lilywhite
	Maki     = 6,   "Maki Nishikino",     Birthday( 4, 19),  Group.Muse, Year.First, Subunit.Bibi

	Honoka   = 1,   "Honoka Kousaka",     Birthday( 8,  3),  Group.Muse, Year.Second, Subunit.Printemps
	Kotori   = 3,   "Kotori Minami",      Birthday( 9, 12),  Group.Muse, Year.Second, Subunit.Printemps
	Umi      = 4,   "Umi Sonoda",         Birthday( 3, 15),  Group.Muse, Year.Second, Subunit.Lilywhite

	Nozomi   = 7,   "Nozomi Toujou",      Birthday( 6,  9),  Group.Muse, Year.Third, Subunit.Lilywhite
	Eli      = 2,   "Eli Ayase",          Birthday(10, 21),  Group.Muse, Year.Third, Subunit.Bibi
	Nico     = 9,   "Nico Yazawa",        Birthday( 7, 22),  Group.Muse, Year.Third, Subunit.Bibi

	# ------------ Uranohoshi / Aqours ------------
	Hanamaru = 107, "Hanamaru Kunikida",  Birthday( 3,  4),  Group.Aqours, Year.First, Subunit.Azalea
	Yoshiko  = 106, "Yoshiko Tsushima",   Birthday( 7, 13),  Group.Aqours, Year.First, Subunit.Guiltykiss
	Ruby     = 109, "Ruby Kurosawa",      Birthday( 9, 21),  Group.Aqours, Year.First, Subunit.Cyaron

	Chika    = 101, "Chika Takami",       Birthday( 8,  1),  Group.Aqours, Year.Second, Subunit.Cyaron
	Riko     = 102, "Riko Sakurauchi",    Birthday( 9, 19),  Group.Aqours, Year.Second, Subunit.Guiltykiss
	You      = 105, "You Watanabe",       Birthday( 4, 17),  Group.Aqours, Year.Second, Subunit.Cyaron

	Kanan    = 103, "Kanan Matsuura",     Birthday( 2, 10),  Group.Aqours, Year.Third, Subunit.Azalea
	Dia      = 104, "Dia Kurosawa",       Birthday( 1,  1),  Group.Aqours, Year.Third, Subunit.Azalea
	Mari     = 108, "Mari Ohara",         Birthday( 6, 13),  Group.Aqours, Year.Third, Subunit.Guiltykiss

	# ------------ Nijigasaki ------------
	Rina     = 209, "Rina Tennouji",      Birthday(11, 13),  Group.Nijigasaki, Year.First, Subunit.Quartz
	Kasumi   = 202, "Kasumi Nakasu",      Birthday( 1, 23),  Group.Nijigasaki, Year.First, Subunit.Quartz
	Shizuku  = 203, "Shizuku Ousaka",     Birthday( 4,  3),  Group.Nijigasaki, Year.First, Subunit.Azuna
	Shioriko = 210, "Shioriko Mifune",    Birthday(10,  5),  Group.Nijigasaki, Year.First, Subunit.Rebirth

	Ayumu    = 201, "Ayumu Uehara",       Birthday( 3,  1),  Group.Nijigasaki, Year.Second, Subunit.Azuna
	Setsuna  = 207, "Setsuna Yuuki",      Birthday( 8,  8),  Group.Nijigasaki, Year.Second, Subunit.Azuna
	Ai       = 205, "Ai Miyashita",       Birthday( 5, 30),  Group.Nijigasaki, Year.Second, Subunit.Diverdiva
	Lanzhu   = 212, "Lanzhu Zhong",       Birthday( 2, 15),  Group.Nijigasaki, Year.Second, Subunit.Rebirth

	Emma     = 208, "Emma Verde",         Birthday( 2,  5),  Group.Nijigasaki, Year.Third, Subunit.Quartz
	Kanata   = 206, "Kanata Konoe",       Birthday(12, 16),  Group.Nijigasaki, Year.Third, Subunit.Quartz
	Karin    = 204, "Karin Asaka",        Birthday( 6, 29),  Group.Nijigasaki, Year.Third, Subunit.Diverdiva
	Mia      = 211, "Mia Taylor",         Birthday(12,  6),  Group.Nijigasaki, Year.Third, Subunit.Rebirth

	# ------------ Liella ------------
	# Kanon    = 301, "Kanon Shibuya",      Birthday( 5,  1),  Group.Liella, Year.Third, Subunit.UnitA
	# Keke     = 302, "Keke Tang",          Birthday( 7, 17),  Group.Liella, Year.Third, Subunit.UnitB
	# Chisato  = 303, "Chisato Arashi",     Birthday( 2, 25),  Group.Liella, Year.Third, Subunit.UnitC
	# Sumire   = 304, "Sumire Heanna",      Birthday( 9, 28),  Group.Liella, Year.Third, Subunit.UnitA
	# Ren      = 305, "Ren Hazuki",         Birthday(11, 24),  Group.Liella, Year.Third, Subunit.UnitB

	# Kinako   = 306, "Kinako Sakurakoji",  Birthday( 4, 10),  Group.Liella, Year.Second, Subunit.UnitC
	# Mei      = 307, "Mei Yoneme",         Birthday(10, 29),  Group.Liella, Year.Second, Subunit.UnitA
	# Shiki    = 308, "Shiki Wakana",       Birthday( 6, 17),  Group.Liella, Year.Second, Subunit.UnitC
	# Natsumi  = 309, "Natsumi Onitsuka",   Birthday( 8, 13),  Group.Liella, Year.Second, Subunit.UnitC

	# Wien     = 310, "Wien Margarete",     Birthday( 1, 20),  Group.Liella, Year.First, Subunit.UnitB
	# Tomari   = 311, "Tomari Onitsuka",    Birthday(12, 28),  Group.Liella, Year.First, Subunit.UnitC
			
	def __getattr__(self, attr):
		if attr == "first_name":
			return self.full_name.split(' ', 1)[0]
			
		if attr == "last_name": 
			return self.full_name.split(' ', 1)[1]
			
		return Enum.__getattribute__(self, attr)
	
	@classmethod
	def get_month_birthdays(cls, month):
		return [member for member in cls if member.birthday.month == month]
	
	@classmethod
	def find_by_birthday(cls, month, day):
		return [member for member in cls if member.birthday.month == month and member.birthday.day == day]


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
	
	
class SortingOrder(Enum):
	Ascending  = 1
	Descending = 2
	
class Ordinal(): pass
class ReleaseDate():
	locale = None
	def __init__(self, locale):
		assert(isinstance(locale, Locale))
		self.locale = locale
	
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
	
class EventType(Enum):
	_init_ = 'value, type_name'
	
	Unset    = 0, "None"
	Story    = 1, "Event"
	Exchange = 2, "Event"
	
	@classmethod
	def from_string(cls, name):
		for e in cls:
			if e.name == name:
				return e
		
		return EventType.Unset
	
class BannerType(Enum):
	_init_ = 'value valid source type_name'
	
	Unset     = 0, False, Source.Unspecified, "None"
	Spotlight = 1, True,  Source.Spotlight,   "Banner"
	Festival  = 2, True,  Source.Festival,    "Banner"
	Party     = 3, True,  Source.Party,       "Banner"
	Other     = 4, False, Source.Unspecified, "Banner"
	Gacha     = 5, False, Source.Gacha,       "Banner"
	
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
