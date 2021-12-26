from enum import Enum
from collections import defaultdict

from .Enums import *

class IdolBase():
	def __init__(self, member_id : Member):
		self.member_id = member_id
		
		self.full_name  = member_id.full_name
		self.first_name = member_id.first_name
		self.last_name  = member_id.last_name
		
		self.group      = member_id.group
		self.year       = member_id.year
		self.subunit    = member_id.subunit
	
	def set(self, idol):
		self.member_id  = idol.member_id
		
		self.full_name  = idol.full_name
		self.first_name = idol.first_name
		self.last_name  = idol.last_name
		
		self.group      = idol.group 
		self.year       = idol.year   
		self.subunit    = idol.subunit
	
	def __str__(self):
		return f"{self.full_name}" #({self.group.displayname} / {self.year.displayname} / {self.subunit.displayname})"
	
	def __repr__(self):
		return f'IdolBase({self.member_id}, "{self.full_name}", {self.group}, {self.year}, {self.subunit})'

class Idols():
	# ------------ Otonokizaka / µ's ------------
	Hanayo   = IdolBase(Member.Hanayo)
	Rin      = IdolBase(Member.Rin)
	Maki     = IdolBase(Member.Maki)

	Honoka   = IdolBase(Member.Honoka)
	Kotori   = IdolBase(Member.Kotori)
	Umi      = IdolBase(Member.Umi)

	Nozomi   = IdolBase(Member.Nozomi)
	Eli      = IdolBase(Member.Eli)
	Nico     = IdolBase(Member.Nico)

	# ------------ Uranohoshi / Aqours ------------
	Hanamaru = IdolBase(Member.Hanamaru)
	Yoshiko  = IdolBase(Member.Yoshiko)
	Ruby     = IdolBase(Member.Ruby)

	Chika    = IdolBase(Member.Chika)
	Riko     = IdolBase(Member.Riko)
	You      = IdolBase(Member.You)

	Kanan    = IdolBase(Member.Kanan)
	Dia      = IdolBase(Member.Dia)
	Mari     = IdolBase(Member.Mari)

	# ------------ Nijigasaki ------------
	Rina     = IdolBase(Member.Rina)
	Kasumi   = IdolBase(Member.Kasumi)
	Shizuku  = IdolBase(Member.Shizuku)
	Shioriko = IdolBase(Member.Shioriko)

	Ayumu    = IdolBase(Member.Ayumu)
	Setsuna  = IdolBase(Member.Setsuna)
	Ai       = IdolBase(Member.Ai)
	Lanzhu   = IdolBase(Member.Lanzhu)

	Emma     = IdolBase(Member.Emma)
	Kanata   = IdolBase(Member.Kanata)
	Karin    = IdolBase(Member.Karin)
	Mia      = IdolBase(Member.Mia)

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
			
			# Add both enum and integer id
			Idols.by_member_id[idol.member_id]         = idol
			Idols.by_member_id[idol.member_id.value]   = idol
			
			Idols.by_year[idol.year].append(idol)
			Idols.by_group[idol.group].append(idol)
			Idols.by_subunit[idol.subunit].append(idol)

Idols.initialize()
