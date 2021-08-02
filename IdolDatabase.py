from enum import Enum
from collections import defaultdict

class Rarity(Enum):
	R  = 10
	SR = 20
	UR = 30

class Type(Enum):
	Vo   = 1
	Sp   = 2
	Gd   = 3
	Sk   = 4

class Attribute(Enum):
	Smile     = 1
	Pure      = 2
	Cool      = 3
	Active    = 4
	Natural   = 5
	Elegant   = 6

class School(Enum):
	Otonokizaka = 1
	Uranohoshi  = 2
	Nijigasaki  = 3
	
class Subunit(Enum):
	Printemps    = 1
	Lilywhite    = 2
	Bibi         = 3
	
	Azalea       = 4
	Cyaron       = 5
	Guiltykiss   = 6
	
	Quartz       = 7
	Diverdiva    = 8
	Azuna        = 9
	Monstergirls = 10
	
	def get_stylized(self):
		return {
			Subunit.Printemps    : "Printemps",
			Subunit.Lilywhite    : "lilywhite",
			Subunit.Bibi         : "BiBi",
			Subunit.Azalea       : "AZALEA",
			Subunit.Cyaron       : "CYaRon!",
			Subunit.Guiltykiss   : "Guilty Kiss",
			Subunit.Quartz       : "QU4RTZ",
			Subunit.Diverdiva    : "DiverDiva",
			Subunit.Azuna        : "AZUNA",
			Subunit.Monstergirls : "Monster Girls",
		}[self]
	
class Year(Enum):
	First  = 1
	Second = 2
	Third  = 3
	
class PassiveEffect(Enum):
	Stamina   = 9
	Appeal    = 10
	Technique = 11

class IdolBase():
	def __init__(self, member_id : int, full_name : str, school : School, year : Year, subunit : Subunit):
		self.MemberId = member_id
		
		self.FullName = full_name
		self.FirstName, self.LastName = full_name.split(' ', 1)
		
		self.School  = school
		self.Year    = year
		self.Subunit = subunit
	
	def set(self, idol):
		self.MemberId = idol.MemberId
		
		self.FullName  = idol.FullName
		self.FirstName = idol.FirstName
		self.LastName  = idol.LastName
		
		self.School  = idol.School 
		self.Year    = idol.Year   
		self.Subunit = idol.Subunit
	
	def __str__(self):
		return f"{self.FullName} ({self.School.name} / {self.Year.name} Year / {self.Subunit.get_stylized()})"
	
	def __repr__(self):
		return f'IdolBase({self.MemberId}, "{self.FullName}", {self.School}, {self.Year}, {self.Subunit})'

class Idols():
	# ------------ Otonokizaka / µ's ------------
	Hanayo   = IdolBase(8,   "Hanayo Koizumi",     School.Otonokizaka, Year.First, Subunit.Printemps)
	Rin      = IdolBase(5,   "Rin Hoshizora",      School.Otonokizaka, Year.First, Subunit.Lilywhite)
	Maki     = IdolBase(6,   "Maki Nishikino",     School.Otonokizaka, Year.First, Subunit.Bibi)

	Honoka   = IdolBase(1,   "Honoka Kousaka",     School.Otonokizaka, Year.Second, Subunit.Printemps)
	Kotori   = IdolBase(3,   "Kotori Minami",      School.Otonokizaka, Year.Second, Subunit.Printemps)
	Umi      = IdolBase(4,   "Umi Sonoda",         School.Otonokizaka, Year.Second, Subunit.Lilywhite)

	Nozomi   = IdolBase(7,   "Nozomi Toujou",      School.Otonokizaka, Year.Third, Subunit.Lilywhite)
	Eli      = IdolBase(2,   "Eli Ayase",          School.Otonokizaka, Year.Third, Subunit.Bibi)
	Nico     = IdolBase(9,   "Nico Yazawa",        School.Otonokizaka, Year.Third, Subunit.Bibi)

	# ------------ Uranohoshi / Aqours ------------
	Hanamaru = IdolBase(107, "Hanamaru Kunikida",  School.Uranohoshi, Year.First, Subunit.Azalea)
	Yoshiko  = IdolBase(106, "Yoshiko Tsushima",   School.Uranohoshi, Year.First, Subunit.Guiltykiss)
	Ruby     = IdolBase(109, "Ruby Kurosawa",      School.Uranohoshi, Year.First, Subunit.Cyaron)

	Chika    = IdolBase(101, "Chika Takami",       School.Uranohoshi, Year.Second, Subunit.Cyaron)
	Riko     = IdolBase(102, "Riko Sakurauchi",    School.Uranohoshi, Year.Second, Subunit.Guiltykiss)
	You      = IdolBase(105, "You Watanabe",       School.Uranohoshi, Year.Second, Subunit.Cyaron)

	Kanan    = IdolBase(103, "Kanan Matsuura",     School.Uranohoshi, Year.Third, Subunit.Azalea)
	Dia      = IdolBase(104, "Dia Kurosawa",       School.Uranohoshi, Year.Third, Subunit.Azalea)
	Mari     = IdolBase(108, "Mari Ohara",         School.Uranohoshi, Year.Third, Subunit.Guiltykiss)

	# ------------ Nijigasaki ------------
	Shizuku  = IdolBase(203, "Shizuku Osaka",      School.Nijigasaki, Year.First, Subunit.Azuna)
	Kasumi   = IdolBase(202, "Kasumi Nakasu",      School.Nijigasaki, Year.First, Subunit.Quartz)
	Rina     = IdolBase(209, "Rina Tennouji",      School.Nijigasaki, Year.First, Subunit.Quartz)
	Shioriko = IdolBase(210, "Shioriko Mifune",    School.Nijigasaki, Year.First, Subunit.Monstergirls)
	Mia      = IdolBase(211, "Mia Taylor",         School.Nijigasaki, Year.First, Subunit.Monstergirls)

	Ayumu    = IdolBase(201, "Ayumu Uehara",       School.Nijigasaki, Year.Second, Subunit.Azuna)
	Setsuna  = IdolBase(207, "Setsuna Yuki",       School.Nijigasaki, Year.Second, Subunit.Azuna)
	Ai       = IdolBase(205, "Ai Miyashita",       School.Nijigasaki, Year.Second, Subunit.Diverdiva)
	Lanzhu   = IdolBase(212, "Lanzhu Zhong",       School.Nijigasaki, Year.Second, Subunit.Monstergirls)

	Emma     = IdolBase(208, "Emma Verde",         School.Nijigasaki, Year.Third, Subunit.Quartz)
	Kanata   = IdolBase(206, "Kanata Konoe",       School.Nijigasaki, Year.Third, Subunit.Quartz)
	Karin    = IdolBase(204, "Karin Asaka",        School.Nijigasaki, Year.Third, Subunit.Diverdiva)

	All         = []
	ByFirstName = {}
	ByMemberId  = {}
	ByYear      = defaultdict(list)
	BySchool    = defaultdict(list)
	BySubunit   = defaultdict(list)
	
	@staticmethod
	def initialize():
		members = [key for key in dir(Idols) if isinstance(getattr(Idols, key), IdolBase)]
		for key in members:
			idol = getattr(Idols, key)
			Idols.All.append(idol)
			
			Idols.ByFirstName[idol.FirstName] = idol
			Idols.ByMemberId[idol.MemberId] = idol
			
			Idols.ByYear[idol.Year].append(idol)
			Idols.BySchool[idol.School].append(idol)
			Idols.BySubunit[idol.Subunit].append(idol)

Idols.initialize()

# for key, idols in Idols.BySchool.items():
# 	print(key)
# 	for idol in idols:
# 		print("  ", idol)
