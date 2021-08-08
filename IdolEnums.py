from enum import Enum

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
	Unset     = 0
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