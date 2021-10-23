from IdolAccessories import *

def percent(value):
	return 1 + value / 100

def calculate_effective_appeal(base_appeal, crit_rate, crit_power):
	return (base_appeal * crit_power * crit_rate) + (base_appeal * (1 - crit_rate))

def calculate_crit_rate(technique, crit_sense):
	return min(1, ((technique * 0.003) + (15 if crit_sense else 0)) / 100)

cp = 180 * 1.34 * 0.01
eli = calculate_effective_appeal(16167 * 1.5 * 0.75, calculate_crit_rate(12301 * 1.5, False), cp)
you = calculate_effective_appeal(13712 * 1.2,        calculate_crit_rate(14277, True), cp)

print(f"Eli {eli}")
print(f"You {you}")

exit()

raw_appeal = 12000
raw_technique = 10000

base_crit_power = 180

accessory_sets = []

accessory_sets.append([Accessories.Brooch.get(), Accessories.Brooch.get(), Accessories.Brooch.get()])
accessory_sets.append([Accessories.Brooch.get(), Accessories.Brooch.get(), Accessories.Bangle.get()])
accessory_sets.append([Accessories.Brooch.get(), Accessories.Bangle.get(), Accessories.Bangle.get()])
accessory_sets.append([Accessories.Bangle.get(limit_break=1), Accessories.Bangle.get(limit_break=3), Accessories.Bangle.get()])

for accessories in accessory_sets:
	brooches = 0
	chokers = 0
	bangles = 0
	accessory_stats = [0, 0, 0]
	for item in accessories:
		parameters = item.get_parameters()
		accessory_stats[0] += parameters[0]
		accessory_stats[1] += parameters[1]
		accessory_stats[2] += parameters[2]
		
		if item.type == AccessoryType.Brooch:
			brooches += item.get_skill_value()
		
		elif item.type == AccessoryType.Choker:
			chokers += item.get_skill_value()
			
		elif item.type == AccessoryType.Bangle:
			bangles += item.get_skill_value()

	crit_power = (base_crit_power + bangles) / 100

	appeal_offset = 0
	technique_offset = 0
	
	for appeal_offset in range(0, 6001, 200):
	# for technique_offset in range(0, 6001, 200):
		# appeal_offset = -technique_offset
		
		base_appeal = (raw_appeal + appeal_offset + accessory_stats[0]) * percent(brooches)
		base_technique = raw_technique + accessory_stats[2]
	
		appeal = base_appeal
		technique = base_technique + technique_offset
		
		crit_sense = (raw_appeal < (raw_technique + technique_offset))
		crit_rate = calculate_crit_rate(technique, crit_sense)
		# print(crit_rate)
		
		effective_appeal = calculate_effective_appeal(appeal, crit_rate, crit_power)
		
		# print(f"{raw_appeal + appeal_offset}, {effective_appeal}")
		# print(f"{raw_technique + technique_offset}, {effective_appeal}")
		print(f"{appeal}, {effective_appeal}")
		# print(f"{appeal}, {effective_appeal}")
		# print(f"{technique}, {appeal}, {appeal * crit_power}")
		# break
		
	print()
	print()
