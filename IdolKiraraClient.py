import requests
import json
import re
import sqlite3 as sqlite
from operator import itemgetter
import time
from datetime import datetime, timezone
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

class KiraraIdolLazyLoader():
	def __init__(self, ordinal):
		self.ordinal = ordinal
		self.data_loaded 
		self.data = {}
	
	def __getitem__(self, key):
		pass
	
# class KiraraIdolSkill():
	
class KiraraIdol():
	def __init__(self, client, data):
		self._client        = client
		
		self.ordinal        = data['ordinal']
		self.id             = data['id']
		
		self.member_id      = Member(data['member_id'])
		self.group_id       = Group(data['group_id'])
		self.subunit_id     = Subunit(data['subunit_id'])
		
		self.normal_name    = data['normal_name']
		self.idolized_name  = data['idolized_name']
		
		self.type           = Type(data['type'])
		self.attribute      = Attribute(data['attribute'])
		self.rarity         = Rarity(data['rarity'])
		
		self.source         = Source(data['source'])
		
		self.release_date   = datetime.fromisoformat(data['release_date'])
		
		try:
			self.data = json.loads(data['json'])
		except IndexError:
			self.data = {}
			# self.data = KiraraIdolLazyLoader()
		
		self.modifiers = (Attribute.Unset, Type.Unset, 1, 1)
	
	def __str__(self):
		idol = Idols.by_member_id[self.member_id]
		return f"「 {self.get_card_name(True)} 」 {self.attribute.name} {self.type.name} {idol}"
	
	def __repr__(self):
		idol = Idols.by_member_id[self.member_id]
		return f"「 {self.get_card_name(True)} 」 {self.attribute.name} {self.type.name} {idol}"
	
	def get_card_name(self, idolized : bool):
		if idolized:
			return self.idolized_name
		else:
			return self.normal_name
	
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
			# Database params
			'''CREATE TABLE `parameters` (
				`key`         TEXT UNIQUE NOT NULL,
				`value`       TEXT,
			    PRIMARY KEY(`key`)
			) WITHOUT ROWID''',
			
			# Idols json table
			'''CREATE TABLE `idols_json` (
			    `ordinal`           INTEGER UNIQUE,
			    `json`              TEXT,
			    PRIMARY KEY(`ordinal`)
			) WITHOUT ROWID''',
			
			# Idols table
			'''CREATE TABLE `idols` (
			    `id`                INTEGER UNIQUE NOT NULL,
			    `ordinal`           INTEGER UNIQUE NOT NULL,
			    `member_id`         INTEGER,
			    `group_id`          INTEGER,
			    `subunit_id`        INTEGER,
			    `normal_name`       TEXT,
			    `idolized_name`     TEXT,
			    `attribute`         INTEGER,
			    `type`              INTEGER,
			    `rarity`            INTEGER,
			    `source`            INTEGER,
			    `release_date`      INTEGER,
			    PRIMARY KEY(`id`, `ordinal`)
			) WITHOUT ROWID''',
			
			# Passive skills
			# '''CREATE TABLE `skills` (
			# 	`skill_id`            INTEGER PRIMARY KEY,
			# 	`name`                TEXT,
			# 	`description`         TEXT,
			# 	`trigger_type`        INTEGER,
			# 	`trigger_probability` INTEGER,
			# 	`effect_type`         INTEGER,
			# 	`target`              INTEGER,
			# 	`levels`              TEXT,
			# ) WITHOUT ROWID''',
			
			# Idols skills table
			# '''CREATE TABLE `idols_skills` (
			#     `ordinal`           INTEGER UNIQUE,
			#     `primary_passive`   INTEGER,
			#     `secondary_passive` INTEGER,
			#     PRIMARY KEY(`ordinal`),
			#     FOREIGN KEY(`primary_passive`)   REFERENCES skills(`id`),
			#     FOREIGN KEY(`secondary_passive`) REFERENCES skills(`id`)
			# ) WITHOUT ROWID''',
		]
		
		for schema in schemas:
			try:
				self.db.execute(schema)
			except sqlite.OperationalError as e:
				error_str = str(e)
				if not ('table' in error_str and 'already exists' in error_str):
					print(schema)
					raise e
				
		self.dbcon.commit()
		
	def database_needs_update(self):
		query = "SELECT value FROM parameters WHERE key = 'last_database_update'"
		self.db.execute(query)
		data = self.db.fetchone()
		if data == None: return True
		
		now = datetime.now(timezone.utc)
		try:
			last_update = datetime.fromisoformat(data['value'])
		except:
			return True
		
		# Update database if it has been over 12 hours
		last_update_seconds = (now - last_update).seconds
		print(f"{last_update_seconds / 3600:0.1f} hours since the last database update.")
		return last_update_seconds > 12 * 3600
		
	def refresh_last_update_time(self):
		query = "INSERT OR REPLACE INTO parameters (key, value) VALUES ('last_database_update', ?)"
		self.db.execute(query, [datetime.now(timezone.utc).isoformat()])
		self.dbcon.commit()
	
	def _make_insert_query(self, table, data):
		columns = ', '.join(data.keys())
		values = ', '.join([f":{key}"  for key in data.keys()])
		return f"""INSERT INTO {table} ({columns}) VALUES ({values})"""
	
	def _make_where_placeholders(self, data):
		return ', '.join(['?'] * len(data))
		
	def _query_idol_data_by_ordinal(self, ordinals):
		query = f"""SELECT * FROM idols_json
		            WHERE ordinal IN ({self._make_where_placeholders(ordinals)})"""
		self.db.execute(query, ordinals)
		
		idols_data = []
		
		existing_ordinals = []
		for ordinal, json_data in self.db.fetchall():
			existing_ordinals.append(ordinal)
			idols_data.append(json.loads(json_data))
			ordinals.remove(ordinal)
		
		print("existing_ordinals", existing_ordinals)
		if existing_ordinals:
			if ordinals:
				print("Some idols were already present in database json archive.")
			else:
				print("All idols were already present in database json archive. No need to query Kirara database.")
		
		if ordinals:
			print("Requesting data from Kirara database...")
			
			query_ordinals = ','.join([str(x) for x in ordinals])
			url = KiraraClient.Endpoints['by_ordinal'].format(query_ordinals)
			r = requests.get(url)
			print("Request result code:", r.status_code)
			
			time.sleep(0.5)
			
			if r.status_code == 404:
				raise KiraraClientNotFound(f"No result with given ordinals: {list(ordinals)}")
			
			if r.status_code != 200:
				raise KiraraClientException("Endpoint status not OK")
			
			response_data = r.json()
			if 'result' not in response_data:
				raise KiraraClientException("Response data does not contain result")
		
			idols_data.extend(response_data['result'])
		
			result_ordinals = set()
			for card in data:
				result_ordinals.add(card['ordinal'])
			
			if not all(x in result_ordinals for x in ordinals):
				partial_result = [x for x in ordinals if x in result_ordinals]
				raise KiraraClientPartialResult(f"Partial result with given ordinals. Missing: {partial_result}")
		
		for card in sorted(idols_data, key=itemgetter('ordinal')):
			idol_info = Idols.by_member_id[card['member']]
			
			if card['ordinal'] not in existing_ordinals:
				serialized = {
					'ordinal'           : card['ordinal'],
					'json'              : json.dumps(card),
				}
				query = self._make_insert_query('idols_json', serialized)
				self.db.execute(query, serialized)
			
			serialized = {
				'id'                : card['id'],
				'ordinal'           : card['ordinal'],
				'member_id'         : card['member'],
				'group_id'          : idol_info.group.value,
				'subunit_id'        : idol_info.subunit.value,
				'normal_name'       : card['normal_appearance']['name'].strip(),
				'idolized_name'     : card['idolized_appearance']['name'].strip(),
				'attribute'         : card['attribute'],
				'type'              : card['role'],
				'rarity'            : card['rarity'],
				'source'            : card['source'],
				'release_date'      : card['release_dates']['jp'],
			}
			query = self._make_insert_query('idols', serialized)
			self.db.execute(query, serialized)
		
		
		# for card in sorted(data['result'], key=itemgetter('ordinal')):
		
		# card_skills = {}
		
		# fields = ["parameter", "values", "target", "target_data"]
		# query_fields = ', '.join([f"'{name}'" for name in fields])
		# query_keys   = ', '.join([f":{name}"  for name in fields])
		
		# for card in data['result']:
		# 	card_skills[card['ordinal']] = [(None, None), (None, None)]
			
		# 	passive_skill = card['passive_skills'][0]
			
		# 	targets_data = [passive_skill['target'], passive_skill['target_2']]
		# 	levels_data = [passive_skill['levels'], passive_skill['levels_2']]
			
		# 	for skill_index, target_data, levels in zip([0, 1], targets_data, levels_data):
		# 		if target_data == None or levels == None:
		# 			assert(target_data == None and levels == None)
		# 			break
				
		# 		parameter = levels[0][1]
		# 		values = [x[2] for x in levels]
				
		# 		# print(target_data)
		# 		target = self.determine_skill_target(target_data, card).value
				
		# 		serialized = {
		# 			'parameter'   : parameter,
		# 			'values'      : json.dumps(values),
		# 			'target'      : target,
		# 			'target_data' : json.dumps(target_data),
		# 		}
				
		# 		query = "INSERT INTO 'skills_passive' ({}) VALUES ({})".format(query_fields, query_keys)
		# 		self.db.execute(query, serialized)
				
		# 		passive_id = self.db.lastrowid
		# 		print(passive_id)
				
		# 		card_skills[card['ordinal']][skill_index] = (passive_id, serialized)
		
		# query_data = []
		
		self.dbcon.commit()
		
		return True
	
	def cache_all_idols(self):
		if not self.database_needs_update():
			print("No need to update database right now.")
			return
			
		self.refresh_last_update_time()
		
		print("Updating database...")
		
		url = KiraraClient.Endpoints['id_list']
		r = requests.get(url)
		if r.status_code != 200:
			raise KiraraClientException("Endpoint status not OK")
		
		response_data = r.json()
		if 'result' not in response_data:
			raise KiraraClientException("Response data does not contain result")
		
		idols_data = response_data['result']
		print(f"Received {len(idols_data)} ordinals from Kirara database.")
		
		missing_ordinals = []
		existing_ordinals = set([x[0] for x in self.db.execute("SELECT ordinal FROM 'idols'")])
		for card in idols_data:
			if card['ordinal'] not in existing_ordinals:
				missing_ordinals.append(card['ordinal'])
		
		print(f"Missing {len(missing_ordinals)} in the local database.")
				
		for ordinals_chunk in chunked(missing_ordinals, 20):
			print("Querying chunk: ", ordinals_chunk)
			self._query_idol_data_by_ordinal(ordinals_chunk)
	
	######################################################################
	
	def get_all_idols(self, with_json = False):
		if with_json:
			query = f"""SELECT idols.*, idols_json.json FROM idols
			            LEFT JOIN idols_json ON idols.ordinal = idols_json.ordinal
			            ORDER BY ordinal"""
		else:
			query = f"""SELECT * FROM idols
			            ORDER BY ordinal"""
		            
		self.db.execute(query)
		return self.convert_to_idol_object(self.db.fetchall())
		
	def get_all_idol_thumbnails(self):
		query = f"""SELECT * FROM idols_json
		            ORDER BY ordinal"""
		self.db.execute(query)
		
		output = []
		for data in self.db.fetchall():
			json_data = json.loads(data['json'])
			output.append(( data['ordinal'], {
				'normal'   : json_data['normal_appearance']['thumbnail_asset_path'],
				'idolized' : json_data['idolized_appearance']['thumbnail_asset_path'],
			}))
		return output
	
	def _get_column_from_type(self, column_type, prefix = None):
		if column_type == None:
			return ""
			
		data_columns = {
			Member    : 'member_id',
			Group     : 'group_id',
			Subunit   : 'subunit_id',
			Type      : 'type',
			Attribute : 'attribute',
			Rarity    : 'rarity',
			Source    : 'source',
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
			query = f"""SELECT * FROM 'idols'
			            WHERE {' AND '.join([x[0] for x in fields])} {group_by}
			            ORDER BY {order_by} {order}"""
			values = [value for x in fields for value in x[1]]
			self.db.execute(query, values)
		else:
			query = f"""SELECT * FROM 'idols' {group_by}
			            ORDER BY {order_by} {order}"""
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
			return (f"{column} IN ({self._make_where_placeholders(data)})", [x.value for x in data])
		else:
			return (f"{column} = ?", [data.value])
	
	def get_newest_idols(self, group : Group = None, rarity : Rarity = None, source : Source = None):
		fields = []
		if group      != None: fields.append(self._make_where_condition("group_id", group))
		if rarity     != None: fields.append(self._make_where_condition("rarity",   rarity))
		if source     != None: fields.append(self._make_where_condition("source",   source))
		
		if fields:
			query = f"""SELECT * FROM 'idols'
			            WHERE ordinal IN (
			            	SELECT MAX(ordinal) FROM 'idols'
			            	WHERE {' AND '.join([x[0] for x in fields])}
			            	GROUP BY member_id
			            )
			            ORDER BY ordinal ASC"""
			# print(query)
			self.db.execute(query, [value for x in fields for value in x[1]])
		else:
			query = f"""SELECT * FROM 'idols'
						WHERE ordinal IN (
							SELECT MAX(ordinal) FROM 'idols'
							GROUP BY member_id
						)
						ORDER BY ordinal ASC"""
			self.db.execute(query)
			
		return self.convert_to_idol_object(self.db.fetchall())
		
	def convert_to_idol_object(self, data):
		return [KiraraIdol(self, x) for x in data]
	
	######################################################################	
	
	def _determine_skill_target(self, target_data, card_data):
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
		
		if isinstance(ordinals, int) or isinstance(ordinals, set):
			ordinals = list(ordinals)
			
		query = f"""SELECT * FROM `idols`
		            WHERE `ordinal` IN ({self._make_where_placeholders(ordinals)})"""
		self.db.execute(query, ordinals)
		
		return self.convert_to_idol_object(self.db.fetchall())
	
	def do_crap(self):
		query = f"SELECT json FROM idols_json ORDER BY ordinal"
		self.db.execute(query)
		
		targets = defaultdict(list)
		for data in self.db.fetchall():
			data = json.loads(data['json'])
			
			for skill_data in data['passive_skills']:
				target_id = int(skill_data['target']['id'])
				target = skill_data['programmatic_target']
				target = re.sub('<[^<]+?>', '', target).strip()
				
				guess = self._determine_skill_target(skill_data['target'], data)
				targets[target_id].append((target, guess))
				
				if skill_data['target_2'] != None:
					if skill_data['target']['id'] != skill_data['target_2']['id']:
						print("LOAL", data['ordinal'], skill_data['target_2']['id'], skill_data['levels_2'][0][1], skill_data['name'], skill_data['programmatic_target'])
				
				# if target_id == 58 and len(target) > 0:
				# 	print(data['ordinal'], target_id, skill_data['name'], skill_data['programmatic_target'])
				
				# if target_id > 1 and target_id < 50:
				# 	print(guess, data['ordinal'], target_id, skill_data['name'], skill_data['programmatic_target'])
		
		for tid, targets in sorted(targets.items(), key=itemgetter(0)):
			print(tid)
			for target, guess in set(targets):
				print(f"\t{target} {guess}")
			print("------------------------------------")
			

if __name__ == "__main__":
	client = KiraraClient()
	client.cache_all_idols()
	# client.do_crap()
	exit()
	
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


# for card in data:
# 	print(card)
# 	print()
# 	card.get_passive_skill()
# 	print("\n----------------------------------------------------------\n")
