import requests
import json
import re
import sqlite3 as sqlite
from operator import itemgetter
import time
from datetime import datetime
import platform

try:
	from backports.datetime_fromisoformat import MonkeyPatch
	MonkeyPatch.patch_fromisoformat()
except Exception as e:
	pass

from IdolDatabase import *

def chunked(seq, size):
	for x in range(0, len(seq), size):
		yield seq[x:x+size]

class KiraraClientException(Exception): pass
class KiraraClientValueError(KiraraClientException): pass

class KiraraClientNotFound(KiraraClientException): pass
class KiraraClientPartialResult(KiraraClientException): pass
	
class KiraraIdol():
	def __init__(self, data):
		self.ordinal      = data['ordinal']
		self.id           = data['id']
		self.member_id    = Member(data['member_id'])
		self.group_id     = Group(data['group_id'])
		self.subunit_id   = Subunit(data['subunit_id'])
		self.type         = Type(data['type'])
		self.attribute    = Attribute(data['attribute'])
		self.rarity       = Rarity(data['rarity'])
		self.source       = Source(data['source'])
		self.release_date = datetime.fromisoformat(data['release_date'])
		self.data         = json.loads(data['json'])
		
		self.modifiers = (Attribute.Unset, Type.Unset, 1, 1)
	
	def __str__(self):
		idol = Idols.by_member_id[self.member_id]
		return f"「 {self.get_card_name(True)} 」 {self.attribute.name} {self.type.name} {idol}"
	
	def __repr__(self):
		idol = Idols.by_member_id[self.member_id]
		return f"「 {self.get_card_name(True)} 」 {self.attribute.name} {self.type.name} {idol}"
	
	def get_card_name(self, idolized : bool):
		if idolized:
			return self.data['idolized_appearance']['name'].strip()
		
		return self.data['normal_appearance']['name']
	
	def set_song_modifiers(self, matching_attribute = Attribute.Unset, matching_type = Type.Unset, modifiers = (1, 1)):
		self.modifiers = (matching_attribute, matching_type, modifiers[0], modifiers[1])
	
	def get_parameters(self, level : int, limit_break : int, with_song_modifiers = False):
		if not (level >= 1 and level <= 100):
			raise KiraraClientValueError("Level must be between 1-100.")
			
		if not (limit_break >= 0 and limit_break <= 5):
			raise KiraraClientValueError("Limit break must be between 0-5")
		
		parameters = (
			self.data["stats"][level - 1][1] + self.data["tt_offset"][limit_break][1] + self.data["idolized_offset"][1],
			self.data["stats"][level - 1][2] + self.data["tt_offset"][limit_break][2] + self.data["idolized_offset"][2],
			self.data["stats"][level - 1][3] + self.data["tt_offset"][limit_break][3] + self.data["idolized_offset"][3],
		)
		
		if with_song_modifiers:
			if self.modifiers[0] != Attribute.Unset:
				if self.modifiers[0] == self.attribute:
					parameters = (parameters[0] * self.modifiers[2], parameters[1] * self.modifiers[2], parameters[2] * self.modifiers[2])
					
				elif self.modifiers[0] != self.attribute:
					parameters = (parameters[0] * self.modifiers[3], parameters[1], parameters[2])
			
			if self.modifiers[1] != Type.Unset and self.modifiers[1] != self.type:
					parameters = (parameters[0] * self.modifiers[3], parameters[1], parameters[2])
			
		return parameters
		
	def zipeffect(self, data):
		keys = [
			"target_parameter",
			"effect_type",
			"effect_value",
			"scale_type",
			"calc_type",
			"timing",
			"finish_type",
			"finish_value",
		]
		return dict(zip(keys, data))
	
	def get_passive_skill(self):
		passive = self.data['passive_skills'][0]
		
		target = {}
		for key, value in passive['target'].items():
			if value:
				target[key] = value
		
		levels = [self.zipeffect(x) for x in passive['levels']]
		# levels = passive['levels']
		
		return passive, target, levels

#-----------------------------------------------------------------------------------------------------------------------

class KiraraClient():
	Database = {}
	
	DatabaseFile = "idols.sqlite"
	
	Endpoints = {
		'id_list'    : "https://allstars.kirara.ca/api/private/cards/id_list.json",
		'by_id'      : "https://allstars.kirara.ca/api/private/cards/id/{}.json",
		'by_ordinal' : "https://allstars.kirara.ca/api/private/cards/ordinal/{}.json",
	}

	def __init__(self):
		self.initialize()

	def initialize(self):
		try:
			self.dbcon = sqlite.connect(KiraraClient.DatabaseFile)
		except:
			print("Failed to open database connection.")
			return False
			
		self.dbcon.row_factory = sqlite.Row
		self.db = self.dbcon.cursor()
		
		self._create_tables()
	
	def _create_tables(self):
		schemas = [
			# Passive skills
			'''CREATE TABLE `passives` (
				`id`          INTEGER PRIMARY KEY AUTOINCREMENT,
				`parameter`   INTEGER,
				`values`      TEXT,
				`target`      INTEGER,
				`target_data` TEXT
			)''',
			
			# Idols table
			'''CREATE TABLE `idols` (
			    `ordinal`           INTEGER UNIQUE,
			    `id`                INTEGER UNIQUE,
			    `member_id`         INTEGER,
			    `group_id`          INTEGER,
			    `subunit_id`        INTEGER,
			    `attribute`         INTEGER,
			    `type`              INTEGER,
			    `rarity`            INTEGER,
			    `source`            INTEGER,
			    `release_date`      INTEGER,
			    `primary_passive`   INTEGER,
			    `secondary_passive` INTEGER,   
			    `json`              TEXT,
			    PRIMARY KEY(`ordinal`, `id`),
			    FOREIGN KEY(`primary_passive`)   REFERENCES passives(`id`),
			    FOREIGN KEY(`secondary_passive`) REFERENCES passives(`id`)
			) WITHOUT ROWID''',
		]
		
		for schema in schemas:
			try:
				self.db.execute(schema)
			except sqlite.OperationalError as e:
				error_str = str(e)
				if not ('table' in error_str and 'already exists' in error_str): raise e
				
		self.dbcon.commit()
	
	def cache_all_idols(self):
		url = KiraraClient.Endpoints['id_list']
		r = requests.get(url)
		if r.status_code != 200:
			raise KiraraClientException("Endpoint status not OK")
		
		data = r.json()
		existing_ordinals = set([x[0] for x in self.db.execute("SELECT ordinal FROM 'idols'")])
		
		ordinals = []
		for card in data['result']:
			if card['ordinal'] not in existing_ordinals:
				ordinals.append(card['ordinal'])
		
		for x in chunked(ordinals, 20):
			print(x)
			self.get_idols_by_ordinal(x)
			time.sleep(0.5)
	
	######################################################################
	
	def get_all_idols(self):
		query = "SELECT * FROM 'idols' ORDER BY ordinal"
		self.db.execute(query)
		return self.convert_to_idol_object(self.db.fetchall())
	
	def _get_column_from_type(self, column_type, prefix = None):
		if column_type == None:
			return ""
			
		data_columns = {
			Member    : 'member_id',
			Type      : 'type',
			Attribute : 'attribute',
			Group     : 'group_id',
			Subunit   : 'subunit_id',
			Source    : 'source',
			Rarity    : 'rarity',
			Ordinal   : 'ordinal',
		}
		if column_type not in data_columns:
			raise KiraraClientException("Column not found or valid")
		
		if prefix:
			return f"{prefix} {data_columns[column_type]}"
		else:
			return data_columns[column_type]
	
	def get_idols(self, member : Member = None,
			type : Type = None, attribute : Attribute = None,
			group : Group = None, subunit : Subunit = None,
			source : Source = None,	rarity : Rarity = None,
			min_rarity : Rarity = None, max_rarity : Rarity = None,
			group_by = None, order_by = Ordinal, order = SortingOrder.Ascending):
	
		fields = []
		if member     != None: fields.append(self._make_where_condition("member_id",  member))
		if type       != None: fields.append(self._make_where_condition("type",       type))
		if attribute  != None: fields.append(self._make_where_condition("attribute",  attribute))
		if group      != None: fields.append(self._make_where_condition("group_id",   group))
		if subunit    != None: fields.append(self._make_where_condition("subunit_id", subunit))
		if source     != None: fields.append(self._make_where_condition("source",     source))
		if rarity     != None: fields.append(self._make_where_condition("rarity",     rarity))
		if min_rarity != None: fields.append(("rarity >= ?",    [min_rarity.value]))
		if max_rarity != None: fields.append(("rarity <= ?",    [max_rarity.value]))
		
		group_by = self._get_column_from_type(group_by, "GROUP BY")
		order_by = self._get_column_from_type(order_by)
		if order == SortingOrder.Ascending:
			order = "ASC"
		else:
			order = "DESC"
		
		if fields:
			query = f"SELECT * FROM 'idols' WHERE {' AND '.join([x[0] for x in fields])} {group_by} ORDER BY {order_by} {order}"
			values = [value for x in fields for value in x[1]]
			self.db.execute(query, values)
		else:
			query = f"SELECT * FROM 'idols' {group_by} ORDER BY {order_by} {order}"
			self.db.execute(query)
			
		return self.convert_to_idol_object(self.db.fetchall())
		
	def get_idols_by_rarity(self, rarity : Rarity):
		return self.get_idols(rarity=rarity)
	
	def get_idols_by_group(self, group : Group, rarity : Rarity = None):
		return self.get_idols(group=group, rarity=rarity)
	
	def get_idols_by_source(self, source : Source, rarity : Rarity = None):
		return self.get_idols(source=source, rarity=rarity)
		
	def _make_where_condition(self, column, data):
		if isinstance(data, list):
			return (f"{column} IN ({', '.join(['?'] * len(data))})", [x.value for x in data])
		else:
			return (f"{column} = ?", [data.value])
	
	def get_newest_idols(self, group : Group = None, rarity : Rarity = None, source : Source = None):
		fields = []
		if group      != None: fields.append(self._make_where_condition("group_id", group))
		if rarity     != None: fields.append(self._make_where_condition("rarity",   rarity))
		if source     != None: fields.append(self._make_where_condition("source",   source))
		
		disgusting_hack = "DESC"
		if platform.system() == 'Linux':
			disgusting_hack = "ASC"
		
		if fields:
			query = f"SELECT * FROM (SELECT * FROM 'idols' ORDER BY ordinal {disgusting_hack}) WHERE {' AND '.join([x[0] for x in fields])} GROUP BY member_id ORDER BY ordinal ASC"
			# print(query)
			values = [value for x in fields for value in x[1]]
			self.db.execute(query, values)
		else:
			query = f"SELECT * FROM (SELECT * FROM 'idols' ORDER BY ordinal {disgusting_hack}) GROUP BY member_id ORDER BY ordinal ASC"
			self.db.execute(query)
			
		return self.convert_to_idol_object(self.db.fetchall())
		
	def convert_to_idol_object(self, data):
		return [KiraraIdol(x) for x in data]
	
	######################################################################	
	
	def determine_skill_target(self, target_data, card_data):
		try:
			assert(len(target_data['fixed_attributes']) == 0)
			assert(len(target_data['fixed_subunits']) == 0)
			assert(len(target_data['fixed_schools']) == 0)
			assert(len(target_data['fixed_years']) == 0)
			assert(len(target_data['fixed_roles']) == 0)
		except:
			print(target_data)
			raise Exception("FIXED DATA ISN'T EMPTY AFTER ALL?")
		
		if   target_data['not_self']        == 1: return SkillTarget.Group
		elif target_data['owner_party']     == 1: return SkillTarget.SameStrategy
		elif target_data['owner_attribute'] == 1: return SkillTarget.SameAttribute
		elif target_data['owner_year']      == 1: return SkillTarget.SameYear
		elif target_data['owner_school']    == 1: return SkillTarget.SameSchool
		elif target_data['owner_role']      == 1: return SkillTarget.SameType
		elif target_data['owner_subunit']   == 1: return SkillTarget.SameSubunit
		elif target_data['self_only']       == 1: return SkillTarget.Self
		elif len(target_data['fixed_members']) > 0:
			assert(len(target_data['fixed_members']) == 1)
			assert(target_data['fixed_members'][0] == card_data['member'])
			return SkillTarget.SameMember
		elif target_data['apply_count'] == 9: return SkillTarget.All
		
		
	def get_idols_by_ordinal(self, ordinals):
		assert isinstance(ordinals, int) or isinstance(ordinals, list) or isinstance(ordinals, set)
		
		if isinstance(ordinals, int):
			ordinals = set([ordinals])
		elif isinstance(ordinals, list) or isinstance(ordinals, set):
			ordinals = set(ordinals)
			
		result = []
		
		# Check for cards in cache database
		query = "SELECT * FROM `idols` WHERE `ordinal` IN ({})".format(', '.join(['?'] * len(ordinals)))
		self.db.execute(query, list(ordinals))
		for idol in self.db.fetchall():
			ordinals.remove(idol['ordinal'])
			result.append(dict(idol))
		
		# If all cards were not found in the database, query them from Kirara endpoint
		if len(ordinals) > 0:
			print("Not found in database", ordinals)
			
			query_ordinals = ','.join([str(x) for x in ordinals])
			url = KiraraClient.Endpoints['by_ordinal'].format(query_ordinals)
			
			r = requests.get(url)
			print(r.status_code)
			if r.status_code == 404:
				raise KiraraClientNotFound(f"No result with given ordinals: {list(ordinals)}")
			
			if r.status_code != 200:
				raise KiraraClientException("Endpoint status not OK")
			
			data = r.json()
			
			result_ordinals = set()
			for card in data['result']:
				result_ordinals.add(card['ordinal'])
			
			if not all(x in result_ordinals for x in ordinals):
				partial_result = [x for x in ordinals if x in result_ordinals]
				raise KiraraClientPartialResult(f"Partial result with given ordinals. Missing: {partial_result}")
			
			card_skills = {}
			
			fields = ["parameter", "values", "target", "target_data"]
			query_fields = ', '.join([f"'{name}'" for name in fields])
			query_keys   = ', '.join([f":{name}"  for name in fields])
			
			for card in data['result']:
				card_skills[card['ordinal']] = [(None, None), (None, None)]
				
				passive_skill = card['passive_skills'][0]
				
				targets_data = [passive_skill['target'], passive_skill['target_2']]
				levels_data = [passive_skill['levels'], passive_skill['levels_2']]
				
				for skill_index, target_data, levels in zip([0, 1], targets_data, levels_data):
					if target_data == None or levels == None:
						assert(target_data == None and levels == None)
						break
					
					parameter = levels[0][1]
					values = [x[2] for x in levels]
					
					# print(target_data)
					target = self.determine_skill_target(target_data, card).value
					
					serialized = {
						'parameter'   : parameter,
						'values'      : json.dumps(values),
						'target'      : target,
						'target_data' : json.dumps(target_data),
					}
					
					query = "INSERT INTO 'passives' ({}) VALUES ({})".format(query_fields, query_keys)
					self.db.execute(query, serialized)
					
					passive_id = self.db.lastrowid
					print(passive_id)
					
					card_skills[card['ordinal']][skill_index] = (passive_id, serialized)
			
			query_data = []
			for card in data['result']:
				skills = card_skills[card['ordinal']]
				
				primary = skills[0][0]
				secondary = skills[1][0]
				
				idol_info = Idols.by_member_id[card['member']]
				
				print(card['ordinal'], card['release_dates'])
				
				serialized = {
					'ordinal'           : card['ordinal'],
					'id'                : card['id'],
					'member_id'         : card['member'],
					'group_id'          : idol_info.group.value,
					'subunit_id'        : idol_info.subunit.value,
					'attribute'         : card['attribute'],
					'type'              : card['role'],
					'rarity'            : card['rarity'],
					'source'            : card['source'],
					'release_date'      : card['release_dates']['jp'],
					'primary_passive'   : primary,
					'secondary_passive' : secondary,
					'json'              : json.dumps(card),
				}
				query_data.append(serialized)
				
			query_data = list(sorted(query_data, key=itemgetter('ordinal')))
			
			fields = [
				"ordinal", "id", "member_id", "group_id", "subunit_id",
				"attribute", "type", "rarity", "source", "release_date",
				"primary_passive", "secondary_passive", "json"
			]
			query_fields = ', '.join([f"`{name}`" for name in fields])
			query_keys   = ', '.join([f":{name}"  for name in fields])
			query = "INSERT INTO `idols` ({}) VALUES ({})".format(query_fields, query_keys)
			self.db.executemany(query, query_data)
			
			self.dbcon.commit()
			
			result.extend(query_data)
		
		return self.convert_to_idol_object(result)


client = KiraraClient()
# client.cache_all_idols()
# exit()

# ids = list(range(400, 515))
# ids = []
# ids.extend([319, 422])
# ids.extend(list(range(160, 170)))
# ids.extend(list(range(300, 310)))
# ids.extend(list(range(450, 470)))
# print(ids)
# data = client.get_idols_by_ordinal(ids)

if __name__ == "__maian__":
	effects = defaultdict(list)

	data = client.get_idols_by_rarity(Rarity.UR)
	for card in data:
		passive, target, levels = card.get_passive_skill()
		target_id = target['id']
		
		effect_type = levels[0]['effect_type']
		# effect_type = levels[0][1]
		
		eff_str = f"{passive['name']} / {passive['programmatic_description'].strip()} / {passive['programmatic_target']}"
		eff_str = re.sub('<[^<]+?>', '', eff_str)
		
		eff = (target, target_id, levels, eff_str)
		effects[effect_type].append(eff)

	for effect_type, effects in effects.items():
		print(effect_type)
		for target, target_id, levels, eff_str in sorted(effects, key=itemgetter(1)):
			levels[0].pop('target_parameter')
			levels[0].pop('finish_value')
			# levels[0].pop('finish_type')
			print(f"  {target_id:<5}{eff_str:<90}{levels[0]}")

# data = client.get_idols_by_ordinal(466)
# for card in data:
# 	print(card)

# data = client.get_idols_by_ordinal([105, 193, 343, 412, 466])
# data = client.get_idols_by_ordinal([455, 42, 41, 343])

# for card in data:
# 	print(card)
# 	print()
# 	card.get_passive_skill()
# 	print("\n----------------------------------------------------------\n")

# print(data)
# params = data.get_parameters(82, 5)
# print(params)
