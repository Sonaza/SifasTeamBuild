from enum import Enum
from collections import defaultdict

from .Enums import *

class IdolBase():
	def __init__(self, member_id : Member):
		self.member_id  = member_id
	
	def set(self, idol):
		self.member_id  = idol.member_id
		
	def __getattr__(self, key):
		if key == 'id':
			return self.member_id.value
		
		return self.member_id.__getattr__(key)
	
	def __str__(self):
		return f"{self.full_name}" #({self.group.display_name} / {self.year.display_name} / {self.subunit.display_name})"
	
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
	
	member_order_by_group = {
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
	member_order = []
	
	@staticmethod
	def initialize():
		Idols.member_order = sum([Idols.member_order_by_group[group] for group in Group], [])
		
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
		
		def sort(unsorted, order):
			output = []
			
			unsorted = dict((x.member_id, x) for x in unsorted)
			for ordered_member_id in order:
				if ordered_member_id in unsorted:
					output.append(unsorted[ordered_member_id])
			
			return output
		
		for key, data in Idols.by_year.items():    Idols.by_year[key]    = sort(Idols.by_year[key], Idols.member_order)
		for key, data in Idols.by_group.items():   Idols.by_group[key]   = sort(Idols.by_group[key], Idols.member_order)
		for key, data in Idols.by_subunit.items(): Idols.by_subunit[key] = sort(Idols.by_subunit[key], Idols.member_order)
		

Idols.initialize()
