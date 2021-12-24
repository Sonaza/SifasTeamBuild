from enum import Enum

class Rarity(Enum):
	R  = 10
	SR = 20
	UR = 30

class Type(Enum):
	Unset = 0
	Vo    = 1
	Sp    = 2
	Gd    = 3
	Sk    = 4

class Attribute(Enum):
	Unset     = 0
	Smile     = 1
	Pure      = 2
	Cool      = 3
	Active    = 4
	Natural   = 5
	Elegant   = 6

class Group(Enum):
	Muse        = 1
	Aqours      = 2
	Nijigasaki  = 3
	
class Member(Enum):
	# ------------ Otonokizaka / µ's ------------
	Hanayo   = 8
	Rin      = 5
	Maki     = 6

	Honoka   = 1
	Kotori   = 3
	Umi      = 4

	Nozomi   = 7
	Eli      = 2
	Nico     = 9

	# ------------ Uranohoshi / Aqours ------------
	Hanamaru = 107
	Yoshiko  = 106
	Ruby     = 109

	Chika    = 101
	Riko     = 102
	You      = 105

	Kanan    = 103
	Dia      = 104
	Mari     = 108

	# ------------ Nijigasaki ------------
	Rina     = 209
	Kasumi   = 202
	Shizuku  = 203
	Shioriko = 210

	Ayumu    = 201
	Setsuna  = 207
	Ai       = 205
	Lanzhu   = 212

	Emma     = 208
	Kanata   = 206
	Karin    = 204
	Mia      = 211
	
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
	Rebirth      = 10
	
	def get_stylized(self):
		return {
			Subunit.Printemps  : "Printemps",
			Subunit.Lilywhite  : "lilywhite",
			Subunit.Bibi       : "BiBi",
			Subunit.Azalea     : "AZALEA",
			Subunit.Cyaron     : "CYaRon!",
			Subunit.Guiltykiss : "Guilty Kiss",
			Subunit.Quartz     : "QU4RTZ",
			Subunit.Diverdiva  : "DiverDiva",
			Subunit.Azuna      : "AZUNA",
			Subunit.Rebirth    : "R3BIRTH",
		}[self]
	
class Year(Enum):
	First  = 1
	Second = 2
	Third  = 3
	
class Source(Enum):
	Unspecified = 1
	Event       = 2
	Gacha       = 3
	GachaP2     = 4 # Unused in API
	Spotlight   = 5
	Festival    = 6
	Party       = 7
	
class SkillTarget(Enum):
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
	
class Ordinal(): pass
class SortingOrder(Enum):
	Ascending  = 1
	Descending = 2
	
