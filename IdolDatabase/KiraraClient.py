import requests
import json
import time
import sqlite3 as sqlite
from operator import itemgetter
from datetime import datetime, timezone

try:
	from backports.datetime_fromisoformat import MonkeyPatch
	MonkeyPatch.patch_fromisoformat()
except Exception as e:
	pass

from .Config import Config
from .Enums import *
from .Idols import *
from .HistoryCrawler import *

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

class KiraraNameSubstitutions():
	normal_name = {
		
	}
	idolized_name = {
		'Mermaid festa vol.1' : 'Mermaid Festa Vol.1',
	}
	
	@classmethod
	def get_normal(cls, name):
		try:
			return cls.normal_name[name]
		except:
			return name
			
	@classmethod
	def get_idolized(cls, name):
		try:
			return cls.idolized_name[name]
		except:
			return name

#-----------------------------------------------------------------------------------------------------------------------

class KiraraIdol():
	def __init__(self, client, data):
		self._client        = client
		
		self.ordinal        = data['ordinal']
		self.id             = data['id']
		
		self.member_id      = Member(data['member_id'])
		self.group_id       = Group(data['group_id'])
		self.subunit_id     = Subunit(data['subunit_id'])
		
		self.normal_name    = KiraraNameSubstitutions.get_normal(data['normal_name'])
		self.idolized_name  = KiraraNameSubstitutions.get_idolized(data['idolized_name'])
		
		self.type           = Type(data['type'])
		self.attribute      = Attribute(data['attribute'])
		self.rarity         = Rarity(data['rarity'])
		
		self.source         = Source(data['source'])
		
		self.release_date   = datetime.fromisoformat(data['release_date'])
		
		try:
			self.event_title  = data['event_title']
		except:
			self.event_title  = None
		
		try:
			self.data = json.loads(data['json'])
		except:
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
	DefaultDatabaseFile = "idols.sqlite"
	
	Endpoints = {
		'id_list'    : "https://allstars.kirara.ca/api/private/cards/id_list.json",
		'by_id'      : "https://allstars.kirara.ca/api/private/cards/id/{}.json",
		'by_ordinal' : "https://allstars.kirara.ca/api/private/cards/ordinal/{}.json",
	}
	
	# -------------------------------------------------------------------------------------------

	def __init__(self, database_file = None):
		if database_file == None:
			self.database_path = KiraraClient.DefaultDatabaseFile
		else:
			self.database_path = database_file
			
		self.initialize()

	def initialize(self):
		try:
			self.dbcon = sqlite.connect(self.database_path)
		except:
			raise KiraraClientException("Failed to open database connection.")
			
		self.dbcon.row_factory = sqlite.Row
		self.db = self.dbcon.cursor()
		
		self._create_tables()
	
	# -------------------------------------------------------------------------------------------
	
	def _create_tables(self):
		from .KiraraDatabaseSchema import schemas
		for schema in schemas:
			try:
				self.db.execute(schema)
				print("Created new table", schema)
				print()
			except sqlite.OperationalError as e:
				error_str = str(e)
				if not ('table' in error_str and 'already exists' in error_str):
					print(schema)
					raise e
				
		self.dbcon.commit()
	
	# -------------------------------------------------------------------------------------------
		
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
	
	# -------------------------------------------------------------------------------------------
	
	def _make_insert_query(self, table, data=None, keys=None):
		if keys == None:
			if data == None: raise KiraraClientValueError("Data can't be None if keys are not explicitly defined.")
			keys = data.keys()
		
		columns = ', '.join(keys)
		values = ', '.join([f":{key}"  for key in keys])
		return f"""INSERT INTO {table} ({columns}) VALUES ({values})"""
		
	def _get_enum_values(self, enum_list):
		return [x.value for x in enum_list]
	
	def _make_where_placeholders(self, data):
		return ', '.join(['?'] * len(data))
	
	# -------------------------------------------------------------------------------------------
	
	def _query_idol_data_by_ordinal(self, requested_ordinals):
		assert isinstance(requested_ordinals, list)
		
		query = f"""SELECT * FROM idols_json
		            WHERE ordinal IN ({self._make_where_placeholders(requested_ordinals)})"""
		self.db.execute(query, requested_ordinals)
		
		idols_data = []
		
		existing_ordinals = []
		for ordinal, json_data in self.db.fetchall():
			existing_ordinals.append(ordinal)
			idols_data.append(json.loads(json_data))
			requested_ordinals.remove(ordinal)
		
		# print("existing_ordinals", existing_ordinals)
		if existing_ordinals:
			if requested_ordinals:
				print("  Some idols were already present in database json archive.")
			else:
				print("  All idols were already present in database json archive. No need to query Kirara database.")
		
		if requested_ordinals:
			print("  Requesting data from Kirara database...")
			
			url = KiraraClient.Endpoints['by_ordinal'].format(','.join([str(x) for x in requested_ordinals]))
			r = requests.get(url, headers={
				'User-Agent' : Config.USER_AGENT,
			})
			# print("Request result code:", r.status_code)
			
			if r.status_code == 404:
				raise KiraraClientNotFound(f"No result with given ordinals: {list(requested_ordinals)}")
			
			if r.status_code != 200:
				raise KiraraClientException("Endpoint status not OK")
			
			response_data = r.json()
			if 'result' not in response_data:
				raise KiraraClientException("Response data does not contain result")
		
			idols_data.extend(response_data['result'])
		
			result_ordinals = set()
			for card in idols_data:
				result_ordinals.add(card['ordinal'])
			
			if not all(x in result_ordinals for x in requested_ordinals):
				partial_result = [x for x in requested_ordinals if x in result_ordinals]
				raise KiraraClientPartialResult(f"Partial result with given ordinals. Missing: {partial_result}")
			
			time.sleep(0.5)
		
		print()
		print("Processing query results...")
		for card in sorted(idols_data, key=itemgetter('ordinal')):
			print(f"  {card['ordinal']:<4} ", end='')
			
			idol_info = Idols.by_member_id[card['member']]
			
			if card['ordinal'] not in existing_ordinals:
				serialized = {
					'ordinal'           : card['ordinal'],
					'json'              : json.dumps(card),
				}
				query = self._make_insert_query('idols_json', serialized)
				self.db.execute(query, serialized)
			
			ordinal_str = str(card['ordinal']);
			
			if card['ordinal'] >= 775 and card['ordinal'] <= 777:
				source = Source.Gacha.value
			elif card['ordinal'] >= 778 and card['ordinal'] <= 780:
				source = Source.Event.value
				
			elif 'source' in card:
				source = card['source']
			elif ordinal_str in self.cards_fallback:
				source = self.cards_fallback[ordinal_str]['source']
			else:
				raise KiraraClientException(f"Card source not determined for ordinal {ordinal_str} in remote data and no fallback found")
			
			if 'release_dates' in card and 'jp' in card['release_dates']:
				release_date = card['release_dates']['jp']
			elif ordinal_str in self.cards_fallback:
				release_date = self.cards_fallback[ordinal_str]['release_date']
			else:
				raise KiraraClientException(f"Card release date not determined for ordinal {ordinal_str} in remote data and no fallback found")
			
			serialized = {
				'id'                : card['id'],
				'ordinal'           : card['ordinal'],
				'member_id'         : card['member'],
				'normal_name'       : card['normal_appearance']['name'].strip(),
				'idolized_name'     : card['idolized_appearance']['name'].strip(),
				'attribute'         : card['attribute'],
				'type'              : card['role'],
				'rarity'            : card['rarity'],
				'source'            : source,
				'release_date'      : release_date,
			}
			query = self._make_insert_query('idols', serialized)
			self.db.execute(query, serialized)
		
		print()
		print("  OK!")
		
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
		print("Processing complete!")
		
		return True
	
	# -------------------------------------------------------------------------------------------
	
	def update_database(self, forced=False):
		if not forced and not self.database_needs_update():
			print("No need to update database right now.")
			return
		
		print("Populating members...")
		self._populate_members_and_metadata()
		
		print()
		print("Retrieving events and banners data...")
		history_data = self._retrieve_history_data()
		
		self.cards_fallback = self._load_cards_data_fallback()
		
		print()
		print("Updating idol database...")
		self._cache_all_idols()
		
		if history_data:
			print()
			print("Updating events and banners database...")
			self._update_history_database(history_data)
			
		self.refresh_last_update_time()
		
	def _load_cards_data_fallback(self):
		try:
			with open(Config.CARD_DATA_FALLBACK, "r", encoding="utf-8") as f:
				return json.load(fp=f)
		except Exception as e:
			print("Failed to load sources fallback file. ", e)
			return {}
			
	# -------------------------------------------------------------------------------------------
	
	def _populate_members_and_metadata(self):
		def executemany(query, data):
			for d in data:
				try:
					self.db.execute(query, d)
				except sqlite.IntegrityError as e:
					if not 'UNIQUE constraint failed' in str(e):
						print(e)
		
		data = []
		for d in Attribute.get_valid():
			data.append({
				'id'         : d.value,
				'name'       : d.name,
			})
		
		query = self._make_insert_query("attributes", data[0])
		executemany(query, data)
		
		# ---------------------
		
		data = []
		for d in Type.get_valid():
			data.append({
				'id'         : d.value,
				'name'       : d.name,
				'full_name'  : d.full_name,
			})
		
		query = self._make_insert_query("types", data[0])
		executemany(query, data)
		
		# ---------------------
		
		data = []
		for d in Group:
			data.append({
				'id'         : d.value,
				'tag'        : d.tag,
				'name'       : d.display_name,
			})
		
		query = self._make_insert_query("groups", data[0])
		executemany(query, data)
		
		# ---------------------
		
		data = []
		for d in Subunit:
			data.append({
				'id'         : d.value,
				'name'       : d.display_name,
			})
		
		query = self._make_insert_query("subunits", data[0])
		executemany(query, data)
		
		# ---------------------
		
		member_data = []
		for member in Member:
			member_data.append({
				'id'         : member.value,
				'name'       : member.full_name,
				'year'       : member.year.value,
				'group_id'   : member.group.value,
				'subunit_id' : member.subunit.value,
			})
		
		query = self._make_insert_query("members", member_data[0])
		executemany(query, member_data)
		
		# ---------------------
		
		self.dbcon.commit()
	
	# -------------------------------------------------------------------------------------------
	
	def _cards_hash(self, ordinals_list):
		return hash(','.join([str(ordinal) for ordinal in ordinals_list]))
	
	def _retrieve_history_data(self):
		query = "SELECT title_en, title_jp FROM events"
		self.db.execute(query)
		known_events = [y for x in self.db.fetchall() for y in (x['title_en'], x['title_jp'])]
		
		query = "SELECT * FROM banner_cards ORDER BY ordinal ASC"
		self.db.execute(query)
		
		known_banners_dict = defaultdict(list)
		for data in self.db.fetchall():
			known_banners_dict[data['banner_id']].append(data['ordinal'])
		
		# known_banners = []
		known_banners_hashes = []
		for banner_id, cards in known_banners_dict.items():
			cards_hash = self._cards_hash(cards)
			# known_banners.append({
			# 	'id'    : banner_id,
			# 	'cards' : cards,
			# 	'hash'  : cards_hash,
			# })
			known_banners_hashes.append(cards_hash)
		
		load_json = 0
		
		if not load_json:
			hc = HistoryCrawler()
			history_result = hc.crawl_history(
				known_events=known_events,
				known_banners_hashes=known_banners_hashes)
		else:
			with open("history.json", "r", encoding="utf-8") as f:
				history_result = json.load(fp=f)
		
		if not history_result:
			print("Found no new event data. Nothing to do...")
			return None
		
		# with open("history.json", "w", encoding="utf-8") as f:
		# 	json.dump(history_result, fp=f)
		
		output_data = {
			'known_events'         : known_events,
			'known_banners_hashes' : known_banners_hashes,
			'history_result'       : history_result,
		}
		return output_data
	
	def _update_history_database(self, data):
		known_events         = data['known_events']
		known_banners_hashes = data['known_banners_hashes']
		history_result       = data['history_result']
		
		event_data = []
		for data in history_result['events']:
			if data['title_en'] in known_events or data['title_jp'] in known_events:
				continue
			data['type'] = EventType.from_string(data['type']).value
			event_data.append(data)
		
		banner_data = []
		for data in history_result['banners']:
			cards_hash = self._cards_hash(data['cards'])
			if cards_hash in known_banners_hashes:
				continue
			
			banner_start = datetime.fromisoformat(data['start_jp'])
			
			card_data = self.get_idols_by_ordinal(data['cards'])
			
			accepted_cards = []
			for card in card_data:
				delta = banner_start - card.release_date
				if delta.days > 0 or delta.seconds > 0:
					continue
				accepted_cards.append(card.ordinal)
			if not accepted_cards:
				continue
			
			data['original_num_cards'] = len(data['cards'])
			
			if len(data['cards']) != len(accepted_cards):
				data['cards'] = accepted_cards
				cards_hash = self._cards_hash(data['cards'])
				if cards_hash in known_banners_hashes:
					continue
				
			data['type'] = BannerType.from_string(data['type']).value
			banner_data.append(data)
				
		if len(event_data) == 0 and len(banner_data) == 0:
			print("Found data but everything is up to date.")
			return
		
		# ------------------------
		# Add events
		
		num_cards = 0
		for data in event_data:
			ordinals = data['cards']
			del data['cards']
			
			event_query = self._make_insert_query('events', data)
			self.db.execute(event_query, data)
			
			cards = [{'event_id': self.db.lastrowid, 'ordinal': ordinal} for ordinal in ordinals]
			
			event_card_query = self._make_insert_query('event_cards', cards[0])
			self.db.executemany(event_card_query, cards)
			
			num_cards += len(cards)
			# print(f"Added event '{data['title_en']}' with {len(cards)} associated cards to database.")
		
		print(f"Added {len(event_data)} events with {num_cards} associated cards to database.")
		
		# ------------------------
		# Add banners
		
		num_cards = 0	
		for data in banner_data:
			ordinals = data['cards']
			del data['cards']
			
			event_query = self._make_insert_query('banners', data)
			self.db.execute(event_query, data)
			
			cards = [{'banner_id': self.db.lastrowid, 'ordinal': ordinal} for ordinal in ordinals]
			
			event_card_query = self._make_insert_query('banner_cards', cards[0])
			self.db.executemany(event_card_query, cards)
			
			num_cards += len(cards)
		
		print(f"Added {len(banner_data)} banners with {num_cards} associated cards to database.")
			
		self.dbcon.commit()
	
	# -------------------------------------------------------------------------------------------
		
	def _cache_all_idols(self):
		url = KiraraClient.Endpoints['id_list']
		r = requests.get(url, headers={
			'User-Agent' : Config.USER_AGENT,
		})
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
		
		print(f"Missing {len(missing_ordinals)} idols in the local database.")
				
		for ordinals_chunk in chunked(missing_ordinals, 20):
			print("Querying ordinals: ", ', '.join([str(x) for x in ordinals_chunk]))
			self._query_idol_data_by_ordinal(ordinals_chunk)
	
	# -------------------------------------------------------------------------------------------
	
	def get_all_idols(self, with_json = False):
		if with_json:
			query = f"""SELECT v_idols.*, idols_json.json FROM 'v_idols'
			            LEFT JOIN idols_json ON v_idols.ordinal = idols_json.ordinal
			            ORDER BY ordinal"""
		else:
			query = f"""SELECT * FROM v_idols
			            ORDER BY ordinal"""
		            
		self.db.execute(query)
		return self.convert_to_idol_object(self.db.fetchall())
	
	# -------------------------------------------------------------------------------------------
		
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
	
	# -------------------------------------------------------------------------------------------
	
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
	
	# -------------------------------------------------------------------------------------------
	
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
			query = f"""SELECT * FROM 'v_idols_with_events'
			            WHERE {' AND '.join([x[0] for x in fields])} {group_by}
			            ORDER BY {order_by} {order}"""
			values = [value for x in fields for value in x[1]]
			self.db.execute(query, values)
		else:
			query = f"""SELECT * FROM 'v_idols_with_events'
			            {group_by}
			            ORDER BY {order_by} {order}"""
			self.db.execute(query)
			
		return self.convert_to_idol_object(self.db.fetchall())
	
	# -------------------------------------------------------------------------------------------
		
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
	
	# -------------------------------------------------------------------------------------------
	
	def get_newest_idols(self, group : Group = None,   rarity : Rarity = None,
		                       source : Source = None, members : Member = [], released_before : datetime = None):
		fields = []
		if group      != None: fields.append(self._make_where_condition("group_id",  group))
		if rarity     != None: fields.append(self._make_where_condition("rarity",    rarity))
		if source     != None: fields.append(self._make_where_condition("source",    source))
		if members:            fields.append(self._make_where_condition("member_id", members))
		
		if released_before != None:
			fields.append((f"release_date <= ?", [released_before.isoformat()]))
		
		if fields:
			query = f"""SELECT * FROM 'v_idols_with_events_and_banner_info_null_allowed'
			            WHERE ordinal IN (
			            	SELECT MAX(ordinal) FROM 'v_idols'
			            	WHERE {' AND '.join([x[0] for x in fields])}
			            	GROUP BY member_id
			            )
			            ORDER BY release_date ASC"""
			# print(query)
			self.db.execute(query, [value for x in fields for value in x[1]])
		else:
			query = f"""SELECT * FROM 'v_idols_with_events_and_banner_info_null_allowed'
						WHERE ordinal IN (
							SELECT MAX(ordinal) FROM 'v_idols'
							GROUP BY member_id
						)
						ORDER BY release_date ASC"""
			self.db.execute(query)
			
		return self.convert_to_idol_object(self.db.fetchall())
		
	# -------------------------------------------------------------------------------------------
	
	# Categories should be a dictionary of tuples with "category name" as the key
	# and value being ([list of rarities], [list of sources]) or None instead of list for any.
	def get_idol_history(self, member : Member, categories, time_now : datetime):
		assert(member != None and isinstance(member, Member))
		
		fields = []
		fields.append(self._make_where_condition("member_id", member))
		
		query = f"""SELECT * FROM v_idols_with_events_and_banner_info_null_allowed
					WHERE {' AND '.join([x[0] for x in fields])}
					ORDER BY release_date ASC"""
		self.db.execute(query, [value for x in fields for value in x[1]])
		
		all_idols = self.convert_to_idol_object(self.db.fetchall())
		
		result = {}
		
		for category_name, (category_rarities, category_sources) in categories.items():
			current_list = []
			
			# Conver to list if not one
			if category_rarities != None and not isinstance(category_rarities, list):
				category_rarities = [category_rarities]
				
			if category_sources != None and not isinstance(category_sources, list):
				category_sources = [category_sources]
			
			previous_idol = None
			
			for idol in all_idols:
				if category_sources != None and idol.source not in category_sources:
					continue
				if category_rarities != None and idol.rarity not in category_rarities:
					continue
				
				time_since_release = time_now - idol.release_date
				
				if previous_idol:
					time_since_previous = idol.release_date - previous_idol.release_date
				else:
					time_since_previous = None
				
				# current_list.append({
				# 	'idol' : idol,
				# 	'time_since_release'  : time_since_release,
				# 	'time_since_previous' : time_since_previous,
				# })
				current_list.append((idol, time_since_release, time_since_previous))
				
				previous_idol = idol
			
			result[category_name] = current_list
		
		return result
	
	# -------------------------------------------------------------------------------------------
	
	def get_events(self):
		query = "SELECT * FROM events ORDER BY start ASC"
		self.db.execute(query)
		
		events = []
		for event in self.db.fetchall():
			event['start'] = datetime.fromisoformat(event['start'])
			event['end'] = datetime.fromisoformat(event['end'])
			event['type'] = EventType(event['type'])
			events.append(event)
		
		return events
	
	# -------------------------------------------------------------------------------------------
	
	def get_events_with_cards(self):
		query = """SELECT * FROM v_idols_with_event_info"""
		self.db.execute(query)
		
		events = defaultdict(lambda: { 'event' : None, 'gacha' : [], 'free': [] })
		for data in self.db.fetchall():
			if not data['event_id']:
				continue
			
			event_id = data['event_id']
			if not events[event_id]['event']:
				events[event_id]['event'] = {
					'title' : data['event_title'],
					'type'  : EventType(data['event_type']),
					'start' : datetime.fromisoformat(data['event_start']),
					'end'   : datetime.fromisoformat(data['event_end']),
				}
			
			card = KiraraIdol(self, data)
			
			if card.source == Source.Event:
				events[event_id]['free'].append(card)
				events[event_id]['free'].sort(key=lambda x: (-x.rarity.value, x.ordinal))
				
			elif card.source == Source.Gacha:
				events[event_id]['gacha'].append(card)
				events[event_id]['gacha'].sort(key=lambda x: (-x.rarity.value, x.ordinal))
			
			else:
				raise KiraraClientException("An unexpected card source for event cards.")
		
		return events
	
	def get_event_features_per_member(self):
		query = """SELECT
		               members.id,
		               COUNT(idols.member_id) AS "times_featured"
		           FROM members
		           LEFT JOIN idols ON idols.member_id = members.id AND idols.source = ? AND idols.rarity = ?
		           LEFT JOIN event_cards ON idols.ordinal = event_cards.ordinal
		           GROUP BY members.id
		           ORDER BY members.id
		        """
		self.db.execute(query, self._get_enum_values([Source.Event, Rarity.UR]))
		
		return dict((Member(x['id']), x['times_featured']) for x in self.db.fetchall())
	
	# -------------------------------------------------------------------------------------------
	
	def _get_card_member_index(self, ordinal):
		query = '''SELECT member_id, rarity, source FROM idols
		           WHERE ordinal = ?'''
		self.db.execute(query, [ordinal])
		
		card = self.db.fetchone()
		
		query = '''SELECT ordinal FROM v_idols
		           WHERE v_idols.member_id = ? AND v_idols.rarity = ? AND v_idols.source = ?
		           ORDER BY v_idols.ordinal'''
		           
		self.db.execute(query, [card['member_id'], card['rarity'], card['source']])
		
		for index, filtered_card in enumerate(self.db.fetchall()):
			if filtered_card['ordinal'] == ordinal:
				return index
		
		return None
	
	def get_banners_with_cards(self):
		query = """SELECT * FROM v_idols_with_banner_info"""
		self.db.execute(query)
		
		banners = defaultdict(lambda: { 'banner' : None, 'cards': [], 'num_others' : None, 'index': -1 })
		for data in self.db.fetchall():
			if not data['banner_id']:
				continue
			
			banner_id = data['banner_id']
			if not banners[banner_id]['banner']:
				banners[banner_id]['banner'] = {
					'title' : data['banner_title'],
					'type'  : BannerType(data['banner_type']),
					'start' : datetime.fromisoformat(data['banner_start']),
					'end'   : datetime.fromisoformat(data['banner_end']),
				}
			
			card = KiraraIdol(self, data)
			
			banners[banner_id]['cards'].append(card)
			banners[banner_id]['cards'].sort(key=lambda x: (-x.rarity.value, x.ordinal))
			
			banners[banner_id]['num_others'] = data['banner_num_cards'] - len(banners[banner_id]['cards'])
			
			if card.rarity == Rarity.UR:
				index = self._get_card_member_index(card.ordinal)
				banners[banner_id]['index'] = max(banners[banner_id]['index'], index)
			
		
		return banners
		
	def get_idols_by_source_and_member(self, sources = [], rarity : Rarity = Rarity.UR):
		assert(sources)
		query = f"""SELECT member_id, COUNT(ordinal) AS num_idols, GROUP_CONCAT(ordinal) AS idol_ordinals FROM idols i
					WHERE source = ? AND rarity = ?
					GROUP BY member_id"""
		
		max_per_source = dict()
		num_idols_by_member = defaultdict(dict)
		for source in sources:
			max_per_source[source] = 0
			
			for member in Member:
				num_idols_by_member[member][source] = {
					'num_idols' : 0,
					'idols'     : [],
				}
			
			self.db.execute(query, [source.value, rarity.value])
			for row in self.db.fetchall():
				member = Member(row['member_id'])
				num_idols_by_member[member][source] = {
					'num_idols' : row['num_idols'],
					'idols'     : [int(x) for x in row['idol_ordinals'].split(',')],
				}
				
				max_per_source[source] = max(row['num_idols'], max_per_source[source])
				
		return num_idols_by_member, max_per_source
		
	# -------------------------------------------------------------------------------------------
		
	def convert_to_idol_object(self, data):
		return [KiraraIdol(self, x) for x in data]
	
	# -------------------------------------------------------------------------------------------
	
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
	
	def get_idols_by_ordinal(self, ordinals, with_json = False):
		assert isinstance(ordinals, int) or isinstance(ordinals, list) or isinstance(ordinals, set)
		
		if isinstance(ordinals, set):
			ordinals = list(ordinals)
		elif isinstance(ordinals, int):
			ordinals = [ordinals]
		
		if with_json:
			query = f"""SELECT v_idols.*, idols_json.json FROM v_idols
			            LEFT JOIN idols_json ON v_idols.ordinal = idols_json.ordinal
			            WHERE v_idols.ordinal IN ({self._make_where_placeholders(ordinals)})"""
		else:
			query = f"""SELECT * FROM v_idols
			            WHERE v_idols.ordinal IN ({self._make_where_placeholders(ordinals)})"""
		self.db.execute(query, ordinals)
		
		return self.convert_to_idol_object(self.db.fetchall())
	
	def do_crap(self):
		import re
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
	
	# -------------------------------------------------------------------------------------------
			

if __name__ == "__main__":
	client = KiraraClient()
	client.cache_all_idols()
	# client.do_crap()
	exit()
	
