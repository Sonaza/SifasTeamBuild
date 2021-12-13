from enum import Enum
from collections import defaultdict

from IdolEnums import *

class IdolBase():
	def __init__(self, member_id : int, full_name : str, group : Group, year : Year, subunit : Subunit):
		self.member_id = member_id
		
		self.full_name = full_name
		self.first_name, self.last_name = full_name.split(' ', 1)
		
		self.group   = group
		self.year    = year
		self.subunit = subunit
	
	def set(self, idol):
		self.member_id = idol.member_id
		
		self.full_name  = idol.full_name
		self.first_name = idol.first_name
		self.last_name  = idol.last_name
		
		self.group   = idol.group 
		self.year    = idol.year   
		self.subunit = idol.subunit
	
	def __str__(self):
		return f"{self.full_name} ({self.group.name} / {self.year.name} year / {self.subunit.get_stylized()})"
	
	def __repr__(self):
		return f'IdolBase({self.member_id}, "{self.full_name}", {self.group}, {self.year}, {self.subunit})'

class Idols():
	# ------------ Otonokizaka / µ's ------------
	Hanayo   = IdolBase(Member.Hanayo,   "Hanayo Koizumi",     Group.Muse, Year.First, Subunit.Printemps)
	Rin      = IdolBase(Member.Rin,      "Rin Hoshizora",      Group.Muse, Year.First, Subunit.Lilywhite)
	Maki     = IdolBase(Member.Maki,     "Maki Nishikino",     Group.Muse, Year.First, Subunit.Bibi)

	Honoka   = IdolBase(Member.Honoka,   "Honoka Kousaka",     Group.Muse, Year.Second, Subunit.Printemps)
	Kotori   = IdolBase(Member.Kotori,   "Kotori Minami",      Group.Muse, Year.Second, Subunit.Printemps)
	Umi      = IdolBase(Member.Umi,      "Umi Sonoda",         Group.Muse, Year.Second, Subunit.Lilywhite)

	Nozomi   = IdolBase(Member.Nozomi,   "Nozomi Toujou",      Group.Muse, Year.Third, Subunit.Lilywhite)
	Eli      = IdolBase(Member.Eli,      "Eli Ayase",          Group.Muse, Year.Third, Subunit.Bibi)
	Nico     = IdolBase(Member.Nico,     "Nico Yazawa",        Group.Muse, Year.Third, Subunit.Bibi)

	# ------------ Uranohoshi / Aqours ------------
	Hanamaru = IdolBase(Member.Hanamaru, "Hanamaru Kunikida",  Group.Aqours, Year.First, Subunit.Azalea)
	Yoshiko  = IdolBase(Member.Yoshiko,  "Yoshiko Tsushima",   Group.Aqours, Year.First, Subunit.Guiltykiss)
	Ruby     = IdolBase(Member.Ruby,     "Ruby Kurosawa",      Group.Aqours, Year.First, Subunit.Cyaron)

	Chika    = IdolBase(Member.Chika,    "Chika Takami",       Group.Aqours, Year.Second, Subunit.Cyaron)
	Riko     = IdolBase(Member.Riko,     "Riko Sakurauchi",    Group.Aqours, Year.Second, Subunit.Guiltykiss)
	You      = IdolBase(Member.You,      "You Watanabe",       Group.Aqours, Year.Second, Subunit.Cyaron)

	Kanan    = IdolBase(Member.Kanan,    "Kanan Matsuura",     Group.Aqours, Year.Third, Subunit.Azalea)
	Dia      = IdolBase(Member.Dia,      "Dia Kurosawa",       Group.Aqours, Year.Third, Subunit.Azalea)
	Mari     = IdolBase(Member.Mari,     "Mari Ohara",         Group.Aqours, Year.Third, Subunit.Guiltykiss)

	# ------------ Nijigasaki ------------
	Rina     = IdolBase(Member.Rina,     "Rina Tennouji",      Group.Nijigasaki, Year.First, Subunit.Quartz)
	Kasumi   = IdolBase(Member.Kasumi,   "Kasumi Nakasu",      Group.Nijigasaki, Year.First, Subunit.Quartz)
	Shizuku  = IdolBase(Member.Shizuku,  "Shizuku Osaka",      Group.Nijigasaki, Year.First, Subunit.Azuna)
	Shioriko = IdolBase(Member.Shioriko, "Shioriko Mifune",    Group.Nijigasaki, Year.First, Subunit.Rebirth)

	Ayumu    = IdolBase(Member.Ayumu,    "Ayumu Uehara",       Group.Nijigasaki, Year.Second, Subunit.Azuna)
	Setsuna  = IdolBase(Member.Setsuna,  "Setsuna Yuki",       Group.Nijigasaki, Year.Second, Subunit.Azuna)
	Ai       = IdolBase(Member.Ai,       "Ai Miyashita",       Group.Nijigasaki, Year.Second, Subunit.Diverdiva)
	Lanzhu   = IdolBase(Member.Lanzhu,   "Lanzhu Zhong",       Group.Nijigasaki, Year.Second, Subunit.Rebirth)

	Emma     = IdolBase(Member.Emma,     "Emma Verde",         Group.Nijigasaki, Year.Third, Subunit.Quartz)
	Kanata   = IdolBase(Member.Kanata,   "Kanata Konoe",       Group.Nijigasaki, Year.Third, Subunit.Quartz)
	Karin    = IdolBase(Member.Karin,    "Karin Asaka",        Group.Nijigasaki, Year.Third, Subunit.Diverdiva)
	Mia      = IdolBase(Member.Mia,      "Mia Taylor",         Group.Nijigasaki, Year.Third, Subunit.Rebirth)

	all_idols     = []
	by_first_name = {}
	by_member_id  = {}
	by_year       = defaultdict(list)
	by_group      = defaultdict(list)
	by_subunit    = defaultdict(list)
	
	member_order = {
		Group.Muse : [
			Member.Hanayo, Member.Rin,    Member.Maki,
			Member.Honoka, Member.Kotori, Member.Umi,
			Member.Nozomi, Member.Eli,    Member.Nico,
		],

		Group.Aqours : [
			Member.Hanamaru, Member.Yoshiko, Member.Ruby, 
			Member.Chika,    Member.Riko,    Member.You, 
			Member.Kanan,    Member.Dia,     Member.Mari, 
		],

		Group.Nijigasaki : [
			Member.Rina,  Member.Kasumi,  Member.Shizuku, Member.Shioriko, 
			Member.Ayumu, Member.Setsuna, Member.Ai,      Member.Lanzhu, 
			Member.Emma,  Member.Kanata,  Member.Karin,   Member.Mia, 
		],
	}
	
	@staticmethod
	def initialize():
		members = [key for key in dir(Idols) if isinstance(getattr(Idols, key), IdolBase)]
		for key in members:
			idol = getattr(Idols, key)
			Idols.all_idols.append(idol)
			
			Idols.by_first_name[idol.first_name] = idol
			Idols.by_member_id[idol.member_id]   = idol
			
			Idols.by_year[idol.year].append(idol)
			Idols.by_group[idol.group].append(idol)
			Idols.by_subunit[idol.subunit].append(idol)

Idols.initialize()


# for key, idols in Idols.By_School.items():
# 	print(key)
# 	for idol in idols:
# 		print("  ", idol)
