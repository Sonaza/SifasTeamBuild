from operator import itemgetter
from enum import Enum

from IdolDatabase import *

client = KiraraClient()

class IdolError(Exception): pass

name_length = 25

class Idol(IdolBase):
	def __init__(self, card_ordinal : int, idol : IdolBase, identifier, crit_power, buff_appeal, buff_technique):
		# super().__init__(idol.FullName, idol.School, idol.Year, idol.Subunit)
		
		self.data = client.get_idols_by_ordinal(card_ordinal, with_json=True)[0]
		
		idol = Idols.by_member_id[self.data.member_id]
		self.set(idol)
		
		self.identifier = identifier
		self.crit_power     = crit_power
		
		self.buff_appeal    = buff_appeal
		self.buff_technique = buff_technique
		
		self._update_parameters()	
	
	def _update_parameters(self):
		self.raw_appeal, self.raw_stamina, self.raw_technique = self.data.get_parameters(80, 5, False)
		self.base_appeal, self.base_stamina, self.base_technique = self.data.get_parameters(80, 5, True)
		
		# Adjust appeal and technique per the buffs
		self.appeal    = self.base_appeal * (1 + self.buff_appeal * 0.01)
		self.technique = self.base_technique * (1 + self.buff_technique * 0.01)
		
		# Cards with technique as the highest stat get extra crit rate
		self.crit_profile   = False
		if self.raw_technique > self.raw_appeal and self.raw_technique > self.raw_stamina:
			self.crit_profile = True
			
		self.crit_rate = min(1, ((self.technique * 0.003) + (15 if self.crit_profile else 0)) * 0.01)
		
		# Calculating the final value
		self.effective_appeal = (self.appeal * self.crit_rate * self.crit_power) + (self.appeal * (1 - self.crit_rate))
	
	def set_song_modifiers(self, matching_attribute = Attribute.Unset, matching_type = Type.Unset, modifiers = (1, 1)):
		self.data.set_song_modifiers(matching_attribute, matching_type, modifiers)
		self._update_parameters()
	
	def __str__(self):
		global name_length
		# return f'    {self.identifier + " " + self.first_name:<{name_length}}    Effective Appeal {self.effective_appeal:5.0f}    Crit Rate {self.crit_rate * 100:5.2f}% ({[" ", "×"][int(self.crit_profile)]})' 
		return f'{self.identifier + " " + self.first_name:<{name_length}}  | {self.effective_appeal:5.0f}   | {self.crit_rate * 100:5.2f}%' 
		
	def __lt__(self, other):
		return self.effective_appeal < other.effective_appeal

#########################################################

number_of_bangles = 2
crit_power = 1.8 * (1 + number_of_bangles * 0.2)

idols = [
	#    Idol                  Identifier         Crit Power   Appeal Buff%  Technique Buff%
	
	## ---------------------------------------
	## Muse
	
	Idol(492, Idols.Rin,       "Tanabata",        crit_power,  3.2,          0.0),
	Idol(412, Idols.Rin,       "Fes2",            crit_power,  7.83,         0.0),
	Idol(442, Idols.Rin,       "Spring",          crit_power,  7.0,          0.0),
	
	Idol(505, Idols.Maki,      "Fes2",            crit_power,  7.0,          0.0),
	
	Idol(566, Idols.Honoka,    "Fes2",            crit_power,  5.2,          0.0),
	
	Idol(373, Idols.Eli,       "Fes2",            crit_power,  7.0,          0.0),
	Idol(593, Idols.Eli,       "Party",           crit_power,  5.2,          2.6),
	
	Idol(144, Idols.Kotori,    "Fes1",            crit_power,  0.0,          5.2),
	Idol(514, Idols.Kotori,    "Party",           crit_power,  8.4,          4.2),
	
	Idol(337, Idols.Nozomi,    "Fes1",            crit_power,  5.2,          0.0),
	Idol(466, Idols.Nozomi,    "Fes2",            crit_power,  7.0,          0.0),
	Idol(193, Idols.Nozomi,    "Magical Fever",   crit_power,  4.2,          0.0),
	
	Idol(164, Idols.Nico,      "Fes1",            crit_power,  0.0,          0.0),
	Idol(392, Idols.Nico,      "Fes2",            crit_power,  5.2,          0.0),
	
	## ---------------------------------------
	## Aqours
	
	Idol(467, Idols.Hanamaru,  "Fes2",            crit_power,  7.0,          0.0),
	
	Idol(504, Idols.Ruby,      "Fes2",            crit_power,  5.2,          0.0),
	Idol(470, Idols.Ruby,      "Rain Blossom",    crit_power,  5.2,          0.0),
	Idol(424, Idols.Ruby,      "Cyber",           crit_power,  5.2,          0.0),
	
	Idol(319, Idols.Kanan,     "Fes1",            crit_power,  9.675,        3.5),
	Idol(48,  Idols.Kanan,     "Initial",         crit_power,  4.2,          0.0),
	
	Idol(262, Idols.Chika,     "Fes1",            crit_power,  7.0,          0.0),
	Idol(523, Idols.Chika,     "Fes2",            crit_power,  5.2,          0.0),
	
	Idol(449, Idols.Riko,      "Fes2",            crit_power,  7.0,          0.0),
	
	Idol(393, Idols.You,       "Fes2",            crit_power,  9.675,        0.0),
	Idol(478, Idols.You,       "Party",           crit_power,  5.2,          0.0),
	
	Idol(181, Idols.Mari,      "Fes1",            crit_power,  7.0,          0.0),
	Idol(181, Idols.Mari,      "Fes1 Proc",       crit_power,  12.35,        0.0),
	
	Idol(547, Idols.Dia,       "Fes2",            crit_power,  5.2,          2.6),
	Idol(422, Idols.Dia,       "Party",           crit_power,  8.4,          0.0),
	Idol(436, Idols.Dia,       "Cherry Blossom",  crit_power,  0.0,          0.0),
	
	## ---------------------------------------
	## Nijigasaki
	
	Idol(487, Idols.Rina,      "Fes2",            crit_power,  4.2,          0.0),
	Idol(454, Idols.Rina,      "Kindergarten",    crit_power,  5.2,          0.0),
	
	Idol(320, Idols.Kasumi,    "Fes1",            crit_power,  5.2,          0.0),
	Idol(375, Idols.Kasumi,    "Fes2",            crit_power,  5.2,          0.0),
	
	Idol(522, Idols.Shizuku,   "Fes2",            crit_power,  15.0,         0.0),
	
	Idol(477, Idols.Shioriko,  "Party",           crit_power,  8.4,          4.2),
	
	Idol(308, Idols.Setsuna,   "Rebel",           crit_power,  8.356,        0.0),
	Idol(146, Idols.Setsuna,   "Fes1",            crit_power,  7.0,          0.0),
	Idol(584, Idols.Setsuna,   "Fes2",            crit_power,  6.5,          3.2),
	Idol(496, Idols.Setsuna,   "Party",           crit_power,  10.2,         2.6),
	
	Idol(402, Idols.Ai,        "Party",           crit_power,  6.5,          0.0),
	
	Idol(182, Idols.Kanata,    "Fes1",            crit_power,  4.2,          0.0),
	Idol(583, Idols.Kanata,    "Fes2",            crit_power,  6.5,          0.0),
	Idol(458, Idols.Kanata,    "Party",           crit_power,  6.5,          0.0),
	
	Idol(163, Idols.Emma,      "Fes1",            crit_power,  0.0,          4.2),
	
	Idol(129, Idols.Karin,     "Fes1",            crit_power,  0.0,          7.0),
	
	Idol(579, Idols.Mia,       "Thanksgiving",    crit_power,  7.0,       0.0),
	Idol(579, Idols.Mia,       "Thanksgiving Proc",    crit_power,  15.025,       0.0),
]

print("Card | Effective Appeal (incl. self buffs) | Crit Rate")
print("-- | -- | --")

for idol in sorted(idols, reverse = True):
	idol.set_song_modifiers(Attribute.Cool, modifiers=(1.2, 0.8))

for idol in sorted(idols, reverse = True):
	if idol.data.type != Type.Sp:
		continue
		
	print(idol)

print()
