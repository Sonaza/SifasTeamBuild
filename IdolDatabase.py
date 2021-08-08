from enum import Enum
from collections import defaultdict

from IdolEnums import *

class IdolBase():
	def __init__(self, member_id : int, full_name : str, school : School, year : Year, subunit : Subunit):
		self.member_id = member_id
		
		self.full_name = full_name
		self.first_name, self.last_name = full_name.split(' ', 1)
		
		self.school  = school
		self.year    = year
		self.subunit = subunit
	
	def set(self, idol):
		self.member_id = idol.member_id
		
		self.full_name  = idol.full_name
		self.first_name = idol.first_name
		self.last_name  = idol.last_name
		
		self.school  = idol.school 
		self.year    = idol.year   
		self.subunit = idol.subunit
	
	def __str__(self):
		return f"{self.full_name} ({self.school.name} / {self.year.name} year / {self.subunit.get_stylized()})"
	
	def __repr__(self):
		return f'IdolBase({self.member_id}, "{self.full_name}", {self.school}, {self.year}, {self.subunit})'

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

	all_idols     = []
	by_first_name = {}
	by_member_id  = {}
	by_year       = defaultdict(list)
	by_school     = defaultdict(list)
	by_subunit    = defaultdict(list)
	
	@staticmethod
	def initialize():
		members = [key for key in dir(Idols) if isinstance(getattr(Idols, key), IdolBase)]
		for key in members:
			idol = getattr(Idols, key)
			Idols.all_idols.append(idol)
			
			Idols.by_first_name[idol.first_name] = idol
			Idols.by_member_id[idol.member_id]   = idol
			
			Idols.by_year[idol.year].append(idol)
			Idols.by_school[idol.school].append(idol)
			Idols.by_subunit[idol.subunit].append(idol)

Idols.initialize()


# for key, idols in Idols.By_School.items():
# 	print(key)
# 	for idol in idols:
# 		print("  ", idol)
