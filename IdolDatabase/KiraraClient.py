import Config
import requests
import json
import time
import sqlite3 as sqlite
import math
import hashlib
from operator import itemgetter
from datetime import datetime, timezone

from colorama import Fore, Style
from collections import defaultdict, namedtuple

from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any, Union


from .Skill import Skill
from .SkillEnum import ST, TT

from CardRotations.Utility import Utility

try:
	from backports.datetime_fromisoformat import MonkeyPatch
	MonkeyPatch.patch_fromisoformat()
except Exception as e:
	pass

# from .Config import Config
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

# @dataclass
# class PassiveSkill():
# 	skill_target     : SkillTarget          = field(init = False)
	
# 	@dataclass
# 	class Effect():
# 		target_parameter : SkillTargetParameter = field(init = False)
# 		effect_value     : float                = field(init = False)
	
# 	skill_effects : List[SkillEffect] = field(init = False, default_factory=list)


class KiraraIdol():
	def __init__(self, client, data):
		self._client        = client
		
		self.build_from_database_row(data)
		
		if self.data:
			self._process_skill_data()
	
	def build_from_database_row(self, data):
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
		
		self.release_date   = self.make_locale_datepair(data, 'release_date')
		
		self.build_event_info(data)
		self.build_banner_info(data)
		
		try:
			self.data = json.loads(data['json'])
		except (IndexError, json.JSONDecodeError):
			self.data = {}
			# self.data = KiraraIdolLazyLoader()
	
	def has_locale_datepair(self, data, key):
		return all([(key + locale.suffix) in data.keys() and data[key + locale.suffix] != None for locale in Locale])
		
	def make_locale_datepair(self, data, key):
		return {locale: datetime.fromisoformat(data[key + locale.suffix]) for locale in Locale}
	
	def build_event_info(self, data):
		self.event = dotdict({
			'id'       : Utility.getter(data, 'event_id',    None),
			'type'     : Utility.getter(data, 'event_type',  None, EventType),
			'title'    : Utility.getter(data, 'event_title', None),
			'start'    : None,
			'end'      : None,
		})
		
		if self.has_locale_datepair(data, 'event_start') and self.has_locale_datepair(data, 'event_end'):
			self.event.start = self.make_locale_datepair(data, 'event_start')
			self.event.end   = self.make_locale_datepair(data, 'event_end')
	
	def build_banner_info(self, data):
		self.banner = dotdict({
			'id'       : Utility.getter(data, 'banner_id',    None),
			'type'     : Utility.getter(data, 'banner_type',  None, BannerType),
			'title'    : Utility.getter(data, 'banner_title', None),
			'start'    : None,
			'end'      : None,
		})
		
		if self.has_locale_datepair(data, 'banner_start') and self.has_locale_datepair(data, 'banner_end'):
			self.banner.start = self.make_locale_datepair(data, 'banner_start')
			self.banner.end   = self.make_locale_datepair(data, 'banner_end')
	
	# ----------------------------------------------------------
	
	def __str__(self):
		# idol = Idols.by_member_id[self.member_id]
		# return f"「 {self.get_card_name(True)} 」 {self.attribute.name} {self.type.name} {idol}"
		return f"{self.member_id.first_name} {self.ordinal}"
	
	def __repr__(self):
		# idol = Idols.by_member_id[self.member_id]
		# return f"「 {self.get_card_name(True)} 」 {self.attribute.name} {self.type.name} {idol}"
		return f"{self.member_id.first_name} {self.ordinal}"
	
	
	def get_card_name(self, idolized : bool):
		if idolized:
			return self.idolized_name
		else:
			return self.normal_name
	
	
	def get_raw_parameters(self, level : int, limit_break : int):
		if not (level >= 1 and level <= 100):
			raise KiraraClientValueError("Level must be between 1-100.")
			
		if not (limit_break >= 0 and limit_break <= 5):
			raise KiraraClientValueError("Limit break must be between 0-5")
		
		parameters = (
			self.data["stats"][level - 1][1] + self.data["tt_offset"][limit_break][1] + self.data["idolized_offset"][1],
			self.data["stats"][level - 1][2] + self.data["tt_offset"][limit_break][2] + self.data["idolized_offset"][2],
			self.data["stats"][level - 1][3] + self.data["tt_offset"][limit_break][3] + self.data["idolized_offset"][3],
		)
			
		return parameters
	
	def _process_skill_data(self):
		def get_skill_object(skill_data):
			del skill_data['is_squashed']
			del skill_data['programmatic_description']
			del skill_data['programmatic_target']
			return Skill(**skill_data)
		
		self.passive_skill = get_skill_object(self.data['passive_skills'][0])
		assert(self.passive_skill.trigger_type == TT.Non)
		
		try:
			self.active_skill = get_skill_object(self.data['passive_skills'][1])
		except IndexError:
			self.active_skill = None
	
	# @dataclass
	# class SkillEffectLevel(object):
	# 	target_parameter : SkillTargetParameter = field(default_factory=SkillTargetParameter)
	# 	effect_type : SkillEffectType = field(default_factory=SkillEffectType)
	# 	effect_value : int
	# 	scale_type : int
	# 	calc_type : int
	# 	timing : int
	# 	finish_type : int
	# 	finish_value : int
	
	def get_passive_skill_effect(self, skill_level):
		max_skill_level = len(self.passive_skill.levels)
		if not (skill_level >= 1 and skill_level <= max_skill_level):
			raise KiraraClientValueError(f"Skill level must be between 1-{max_skill_level}")
			
		passive = self.data['passive_skills'][0]
		skill_target = self._determine_skill_target(self.passive_skill.target)
		
		if self.passive_skill.target_2 != None:
			assert(skill_target == self._determine_skill_target(self.passive_skill.target_2))
		
		# print(skill_target)
		
		effects = []
		for levels in [self.passive_skill.levels, self.passive_skill.levels_2]:
			if levels == None:
				continue
			
			effect = Skill.Effect._make(levels[skill_level - 1])
			effects.append(dotdict({
				"effect_type"   : SkillEffectType(effect.effect_type),
				"effect_value"  : effect.effect_value / 100,
			}))
		
		# print(effects)
		return skill_target, effects
		
	def _determine_skill_target(self, target_data):
		try:
			assert(len(target_data['fixed_attributes']) == 0)
			assert(len(target_data['fixed_subunits']) == 0)
			assert(len(target_data['fixed_schools']) == 0)
			assert(len(target_data['fixed_years']) == 0)
			assert(len(target_data['fixed_roles']) == 0)
		except:
			print(target_data)
			raise Exception("FIXED DATA ISN'T EMPTY AFTER ALL?")
		
		if   target_data['not_self']        == 1:
			return SkillTarget.Group
		elif target_data['owner_party']     == 1:
			return SkillTarget.SameStrategy
		elif target_data['owner_attribute'] == 1:
			return SkillTarget.SameAttribute
		elif target_data['owner_year']      == 1:
			return SkillTarget.SameYear
		elif target_data['owner_school']    == 1:
			return SkillTarget.SameSchool
		elif target_data['owner_role']      == 1:
			return SkillTarget.SameType
		elif target_data['owner_subunit']   == 1:
			return SkillTarget.SameSubunit
		elif target_data['self_only']       == 1:
			return SkillTarget.Self
		elif len(target_data['fixed_members']) > 0:
			assert(len(target_data['fixed_members']) == 1)
			assert(target_data['fixed_members'][0] == self.member_id.value)
			return SkillTarget.SameMember
		elif target_data['apply_count'] == 9:
			return SkillTarget.All
		
		print(target_data)
		raise Exception("Something is not handled?")
		return SkillTarget.Unknown

#-----------------------------------------------------------------------------------------------------------------------

class KiraraClient():
	Endpoints = {
		'id_list'    : "https://allstars.kirara.ca/api/private/cards/id_list.json",
		'by_id'      : "https://allstars.kirara.ca/api/private/cards/id/{}.json",
		'by_ordinal' : "https://allstars.kirara.ca/api/private/cards/ordinal/{}.json",
	}
	
	# -------------------------------------------------------------------------------------------

	def __init__(self, database_file = None):
		self.database_path = Config.DATABASE_FILE
		self.initialize()

	def initialize(self):
		self._initialize_member_addition_dates()
		
		self.database_was_updated = False
		
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
				print("Executed SQL:", schema)
				print()
			except sqlite.OperationalError as e:
				error_str = str(e)
				if not ('already exists' in error_str):
					print(schema)
					raise e
				
		self.dbcon.commit()
	
	# -------------------------------------------------------------------------------------------
	
	def get_database_update_time(self):
		query = "SELECT value FROM parameters WHERE key = 'last_database_update'"
		self.db.execute(query)
		
		data = self.db.fetchone()
		if data == None:
			return None
		
		try:
			last_update = datetime.fromisoformat(data['value'])
		except:
			return None
		
		return last_update
	
	def database_needs_update(self):
		last_update = self.get_database_update_time()
		if last_update == None:
			return True
		
		# Update database if it has been over 18 hours
		now = datetime.now(timezone.utc)
		last_update_seconds = (now - last_update).seconds
		print(f"{Fore.YELLOW}{Style.BRIGHT}{last_update_seconds / 3600:0.1f} hours since the last database update.{Style.RESET_ALL}")
		return last_update_seconds > 18 * 3600
		
	def refresh_last_update_time(self):
		query = "INSERT OR REPLACE INTO parameters (key, value) VALUES ('last_database_update', ?)"
		self.db.execute(query, [datetime.now(timezone.utc).isoformat()])
		self.dbcon.commit()
	
	# -------------------------------------------------------------------------------------------
	
	def _make_insert_query(self, table, data=None, keys=None, update_insert=False):
		if keys == None:
			if data == None: raise KiraraClientValueError("Data can't be None if keys are not explicitly defined.")
			keys = data.keys()
		
		columns = ', '.join(keys)
		values = ', '.join([f":{key}"  for key in keys])
		
		if update_insert:
			return f"""INSERT OR REPLACE INTO {table} ({columns}) VALUES ({values})"""
		else:
			return f"""INSERT INTO {table} ({columns}) VALUES ({values})"""
		
	def _get_enum_values(self, enum_list):
		return [x.value for x in enum_list]
	
	def _make_where_placeholders(self, data):
		return ', '.join(['?'] * len(data))
	
	# -------------------------------------------------------------------------------------------
		
	def cache_all_idols(self, rescrape_days):
		missing_ordinals = self.get_missing_ordinals()
		if missing_ordinals:
			print(f"  {Fore.YELLOW}{Style.BRIGHT}Missing from database{Fore.WHITE}   : {len(missing_ordinals)} idols{Style.RESET_ALL}")
			with print_indent(4):
				for index, ordinals_chunk in enumerate(chunked(missing_ordinals, 20)):
					print(f"{Fore.YELLOW}{Style.BRIGHT}Batch {index + 1:>2}{Fore.WHITE}  : {Utility.concat(ordinals_chunk, separator=', ', last_separator=' and ')}")
					self.query_idol_data_by_ordinal(ordinals_chunk, rescrape=False)
		
		rescrape_ordinals = self.get_ordinals_to_rescrape(rescrape_days, missing_ordinals)
		if rescrape_ordinals:
			print(f"  {Fore.CYAN}{Style.BRIGHT}Rescraping for updates{Fore.WHITE}  : {len(rescrape_ordinals)} idols{Style.RESET_ALL}")
			with print_indent(4):
				for index, ordinals_chunk in enumerate(chunked(rescrape_ordinals, 20)):
					print(f"{Fore.YELLOW}{Style.BRIGHT}Batch {index + 1:>2}{Fore.WHITE}  : {Utility.concat(ordinals_chunk, separator=', ', last_separator=' and ')}")
					self.query_idol_data_by_ordinal(ordinals_chunk, rescrape=True)
	
	
	def get_missing_ordinals(self):
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
		print(f"  {Fore.YELLOW}{Style.BRIGHT}Received {len(idols_data)} ordinals from Kirara database.")
		
		existing_ordinals = set([x[0] for x in self.db.execute("SELECT ordinal FROM 'idols'")])
		return [int(card['ordinal']) for card in idols_data if card['ordinal'] not in existing_ordinals]
		
		
	def get_ordinals_to_rescrape(self, rescrape_days, excluded_ordinals=[]):
		if rescrape_days <= 0:
			return []
			
		scrape_threshold = datetime.now(tz=timezone.utc) - timedelta(days=rescrape_days, hours=1)
		
		query = "SELECT ordinal FROM idols WHERE release_date_jp >= ?"
		self.db.execute(query, [scrape_threshold.isoformat()])
		return [int(data['ordinal']) for data in self.db.fetchall() if int(data['ordinal']) not in excluded_ordinals]
	
	
	def query_idol_data_by_ordinal(self, requested_ordinals : List[int], rescrape : bool = False):
		assert isinstance(requested_ordinals, list)
		
		query = f"""SELECT ordinal, json FROM idols_json
					WHERE ordinal IN ({self._make_where_placeholders(requested_ordinals)})"""
		self.db.execute(query, requested_ordinals)
		
		existing_idols_data = {}
		
		existing_ordinals = []
		for ordinal, json_data in self.db.fetchall():
			ordinal = int(ordinal)
			existing_ordinals.append(ordinal)
			
			json_data_hash = hashlib.sha1(json_data.encode('utf-8')).hexdigest()
			try:
				json_data_parsed = json.loads(json_data)
			except json.JSONDecodeError:
				raise KiraraClientException("JSON from the database could not be parsed.")
			
			existing_idols_data[ordinal] = {
				'hash' : json_data_hash,
				'data' : json_data_parsed,
			}
			
			if rescrape == False:
				requested_ordinals.remove(ordinal)
		
		
		if not rescrape and existing_ordinals:
			if requested_ordinals:
				print("  Some idols were already present in database JSON archive.")
			else:
				print("  All idols were already present in database JSON archive. No need to query Kirara database.")
		
		elif rescrape:
			if len(requested_ordinals) == len(existing_ordinals):
				print("  All rescraped idols were present in database JSON archive.")
			else:
				print("  Some rescraped idols were not present in database JSON archive.")
		
		# -------------------------------------------
		
		requested_idols_data = {}
		
		if requested_ordinals:
			print(f"  {Fore.BLUE}{Style.BRIGHT}Requesting data from Kirara database...{Style.RESET_ALL}")
			
			# url = KiraraClient.Endpoints['by_ordinal'].format(','.join([str(x) for x in requested_ordinals]))
			url = KiraraClient.Endpoints['by_ordinal'].format(Utility.concat(requested_ordinals))
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
		
			for idol_data in sorted(response_data['result'], key=itemgetter('ordinal')):
				ordinal = int(idol_data['ordinal'])
				requested_idols_data[ordinal] = idol_data
			
			result_ordinals = set(requested_idols_data.keys())
			
			if not Utility.contains_all(result_ordinals, requested_ordinals):
				partial_result = [ordinal for ordinal in requested_ordinals if ordinal not in result_ordinals]
				raise KiraraClientPartialResult(f"Partial result with given ordinals. Missing: {partial_result}")
			
			# time.sleep(0.5)
		
		print_indent.add(4)
		
		if not rescrape and existing_idols_data:
			print("  Restoring old cached idol data:")
			for index, (ordinal, existing_idol) in enumerate(existing_idols_data.items()):
				print(f"{Fore.WHITE}{ordinal:>4}{Style.RESET_ALL}", end='  ')
				self.update_idol_database_entry(ordinal, existing_idol['data'])
				if (index + 1) % 5 == 0 and (index + 1) != len(existing_idols_data): print()
			print()
		
		for index, (ordinal, idol_data) in enumerate(requested_idols_data.items()):
			print(f"{Fore.WHITE}{ordinal:>4}{Style.RESET_ALL}", end=' ')
			
			update_entry = True
			if rescrape or ordinal not in existing_ordinals:
				serialized = {
					'ordinal'  : ordinal,
					'json'     : json.dumps(idol_data),
				}
				json_data_hash = hashlib.sha1(serialized['json'].encode('utf-8')).hexdigest()
				
				if ordinal not in existing_ordinals or json_data_hash != existing_idols_data[ordinal]['hash']:
					query = self._make_insert_query('idols_json', serialized, update_insert=True)
					self.db.execute(query, serialized)
				
				if rescrape:
					if json_data_hash == existing_idols_data[ordinal]['hash']:
						print(f"{Fore.BLACK}{Style.BRIGHT}(OK){Style.RESET_ALL}", end='  ')
						update_entry = False
					else:
						print(f"{Fore.GREEN}{Style.BRIGHT}(!!){Style.RESET_ALL}", end='  ')
			
			if update_entry:
				self.update_idol_database_entry(ordinal, idol_data, overwrite=rescrape)
			
			if (index + 1) % 5 == 0 and (index + 1) < len(requested_idols_data):
				print()
		
		print_indent.reduce(4)
		
		print()
		print("  OK!")
		
		self.dbcon.commit()
		print("Processing complete!")
		
		return True
		
	
	def update_idol_database_entry(self, ordinal : int, idol_data : Dict[Any, Any], overwrite : bool = False):
		ordinal_str = str(idol_data['ordinal']);
		
		# -------------------------------------------------
		# Retrieve card source
		
		if 'source' in idol_data:
			source = idol_data['source']
		elif ordinal_str in self.cards_fallback:
			source = self.cards_fallback[ordinal_str]['source']
		else:
			raise KiraraClientException(f"Card source not determined for ordinal {ordinal_str} in remote data and no fallback found")
		
		# -------------------------------------------------
		# Retrieve release date
		
		release_dates = {
			Locale.JP : None,
			Locale.WW : None,
		}
		
		member    = Member(idol_data['member'])
		
		check_fallbacks = False
		if 'release_dates' in idol_data:
			if 'jp' in idol_data['release_dates']:
				release_dates[Locale.JP] = idol_data['release_dates']['jp']
			else:
				check_fallbacks = True
				
			if 'en' in idol_data['release_dates']:
				release_dates[Locale.WW] = idol_data['release_dates']['en']
			else:
				check_fallbacks = True
		
		if check_fallbacks:
			if ordinal_str in self.cards_fallback:
				if release_dates[Locale.JP] == None:
					release_dates[Locale.JP] = self.cards_fallback[ordinal_str]['release_date_jp']
					
				if release_dates[Locale.WW] == None:
					release_dates[Locale.WW] = self.cards_fallback[ordinal_str]['release_date_ww']
			
			# Fallbacks for Shioriko R cards, they don't seem to have global release date
			released_on_member_addition = [284, 285]
			if idol_data['ordinal'] in released_on_member_addition:
				release_dates[Locale.JP] = self.member_addition_dates[Locale.JP][member]['date_added'].isoformat()
				release_dates[Locale.WW] = self.member_addition_dates[Locale.WW][member]['date_added'].isoformat()
			
		if release_dates[Locale.JP] == None or release_dates[Locale.WW] == None:
			raise KiraraClientException(f"Unable to identify a card release date for ordinal {ordinal_str}.")
				
		# Just guarantee release dates don't go before member addition date for some reason
		for locale in Locale:
			date = datetime.fromisoformat(release_dates[locale])
			if date < self.member_addition_dates[locale][member]['date_added']:
				release_dates[locale] = self.member_addition_dates[locale][member]['date_added'].isoformat()
		
		# -------------------------------------------------
		
		serialized = {
			'id'                : idol_data['id'],
			'ordinal'           : idol_data['ordinal'],
			'member_id'         : idol_data['member'],
			'normal_name'       : idol_data['normal_appearance']['name'].strip(),
			'idolized_name'     : idol_data['idolized_appearance']['name'].strip(),
			'attribute'         : idol_data['attribute'],
			'type'              : idol_data['role'],
			'rarity'            : idol_data['rarity'],
			'source'            : source,
			'release_date_jp'   : release_dates[Locale.JP],
			'release_date_ww'   : release_dates[Locale.WW],
		}
		query = self._make_insert_query('idols', serialized, update_insert=overwrite)
		self.db.execute(query, serialized)
	
	# -------------------------------------------------------------------------------------------
	
	def database_updated(self):
		return self.database_was_updated
	
	def update_database(self, forced_update=False, load_history_from_file=False, rescrape_days=14):
		if not forced_update and not self.database_needs_update():
			print(f"  {Fore.BLACK}{Style.BRIGHT}No need to update database right now.{Style.RESET_ALL}")
			return False
		
		self.populate_members_and_metadata()
		
		# print()
		# print(f"{Fore.BLUE}{Style.BRIGHT}Retrieving events and banners data...{Style.RESET_ALL}")
		# history_data = self.retrieve_history_data(load_from_file=load_history_from_file)
		
		self.cards_fallback = self.load_cards_data_fallback()
		
		print()
		print(f"{Fore.BLUE}{Style.BRIGHT}Updating idol database...{Style.RESET_ALL}")
		self.cache_all_idols(rescrape_days=rescrape_days)
		
		# if history_data:
		# 	print()
		# 	print(f"{Fore.BLUE}{Style.BRIGHT}Updating events and banners database...{Style.RESET_ALL}")
		# 	self.update_history_database(history_data)
			
		self.refresh_last_update_time()
		self.database_was_updated = True
		
		return True
		
	def load_cards_data_fallback(self):
		try:
			with open(Config.DATA_FALLBACK_FILE, "r", encoding="utf-8") as f:
				return json.load(fp=f)
		except Exception as e:
			print(f"  {Fore.RED}Failed to load sources fallback file: {e}{Style.RESET_ALL}")
			return {}
			
	# -------------------------------------------------------------------------------------------
	
	def populate_members_and_metadata(self):
		anything_changed = False
		
		def executemany(query, data):
			for d in data:
				try:
					self.db.execute(query, d)
					anything_changed = True
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
		
		if anything_changed:
			print(f"{Fore.BLUE}{Style.BRIGHT}Populated members and metadata...{Style.RESET_ALL}")
	
	# -------------------------------------------------------------------------------------------
	
	def append_to_history_data(self, new_entries):
		try:
			with open(Config.HISTORY_CRAWL_FILE, "r", encoding="utf-8") as file:
				history_data = json.load(fp=file)
		except:
			with open(Config.HISTORY_CRAWL_FILE, "w", encoding="utf-8") as file:
				json.dump(new_entries, fp=file)
			return
		
		known_event_hashes  = set([event['cards_hash'] for event in history_data['events']])
		for event in new_entries['events']:
			if event['cards_hash'] in known_event_hashes: continue
			history_data['events'].append(event)
		history_data['events'].sort(key=itemgetter('start_jp'))
			
		known_banner_hashes = set([banner['cards_hash'] for banner in history_data['banners']])
		for banner in new_entries['banners']:
			if banner['cards_hash'] in known_banner_hashes: continue
			history_data['banners'].append(banner)
		history_data['banners'].sort(key=itemgetter('start_jp'))
		
		with open(Config.HISTORY_CRAWL_FILE, "w", encoding="utf-8") as file:
			json.dump(history_data, fp=file)
	
	
	def retrieve_history_data(self, load_from_file=False):
		query = "SELECT title_ww, title_jp FROM events"
		self.db.execute(query)
		known_events = [title for event in self.db.fetchall() for title in (event['title_ww'], event['title_jp'])]
		
		query = "SELECT cards_hash FROM banners"
		self.db.execute(query)
		known_banners_hashes = [data['cards_hash'] for data in self.db.fetchall()]
		
		if not load_from_file:
			hc = HistoryCrawler()
			new_history_entries = hc.crawl_history(
				known_events         = known_events,
				known_banners_hashes = known_banners_hashes)
			
			self.append_to_history_data(new_history_entries)
			
		else:
			print(f"  {Fore.YELLOW}{Style.BRIGHT}Loading history data from file{Style.RESET_ALL}  ...  ", end='')
			try:
				with open(Config.HISTORY_CRAWL_FILE, "r", encoding="utf-8") as file:
					new_history_entries = json.load(fp=file)
				print(f"{Fore.GREEN}{Style.BRIGHT}Success!{Style.RESET_ALL}")
			except:
				print(f"{Fore.RED}{Style.BRIGHT}Failed!   Proceeding without history data.{Style.RESET_ALL}")
			return None
		
		if not new_history_entries['events'] and not new_history_entries['banners']:
			print(f"  {Fore.MAGENTA}{Style.BRIGHT}Found no new event data. Nothing to do...{Style.RESET_ALL}")
			return None
		
		output_data = {
			'known_events'         : known_events,
			'known_banners_hashes' : known_banners_hashes,
			'history_result'       : new_history_entries,
		}
		return output_data
		
	
	def update_history_database(self, data):
		known_events         = data['known_events']
		known_banners_hashes = data['known_banners_hashes']
		history_result       = data['history_result']
		
		event_data = []
		for data in history_result['events']:
			if data['title_ww'] in known_events or data['title_jp'] in known_events:
				continue
			data['type'] = EventType.from_string(data['type']).value
			event_data.append(data)
		
		banner_data = []
		for data in history_result['banners']:
			if data['cards_hash'] in known_banners_hashes:
				continue
			
			banner_start_jp = datetime.fromisoformat(data['start_jp'])
			
			card_data = self.get_idols_by_ordinal(data['cards'])
			
			# Excludes cards from banners that did not initially release with it
			accepted_cards = []
			for card in card_data:
				delta = banner_start_jp - card.release_date[Locale.JP]
				if delta.days > 0 or delta.seconds > 0:
					continue
				accepted_cards.append(card.ordinal)
				
			# And if all were excluded the banner is rejected as a full re-run
			if not accepted_cards:
				continue
			
			# But save the number of cards the banner originally had
			data['original_num_cards'] = len(data['cards'])
			
			# Need to recompute hash if cards were rejected and check if the banner is known
			if len(data['cards']) != len(accepted_cards):
				data['cards'] = accepted_cards
				cards_hash = HistoryCrawler.hash_ordinals(data['cards'])
				if cards_hash in known_banners_hashes:
					continue
				
				data['cards_hash'] = cards_hash
			
			data['type'] = BannerType.from_string(data['type']).value
			banner_data.append(data)
				
		if len(event_data) == 0 and len(banner_data) == 0:
			print(f"  {Fore.BLACK}{Style.BRIGHT}Everything is up to date.{Style.RESET_ALL}")
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
			# print(f"Added event '{data['title_ww']}' with {len(cards)} associated cards to database.")
		
		print(f"  {Fore.GREEN}{Style.BRIGHT}Added {len(event_data)} events with {num_cards} associated cards to the database.{Style.RESET_ALL}")
		
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
		
		print(f"  {Fore.GREEN}{Style.BRIGHT}Added {len(banner_data)} banners with {num_cards} associated cards to the database.{Style.RESET_ALL}")
			
		self.dbcon.commit()
	
	# -------------------------------------------------------------------------------------------
	
	def get_idol_ordinals_with_json(self):
		query = f"""SELECT v_idols.ordinal AS ordinal, v_idols.member_id AS member_id, idols_json.json AS json FROM 'v_idols'
					LEFT JOIN idols_json ON v_idols.ordinal = idols_json.ordinal
					ORDER BY v_idols.ordinal"""
					
		self.db.execute(query)
		
		result = []
		for data in self.db.fetchall():
			try:
				result.append((
					data['ordinal'],
					data['member_id'],
					json.loads(data['json']),
				))
			except json.JSONDecodeError:
				pass
		
		return result
		
		
	def get_all_idols(self, with_json = False):
		if with_json:
			query = f"""SELECT v_idols.*, idols_json.json FROM 'v_idols'
						LEFT JOIN idols_json ON v_idols.ordinal = idols_json.ordinal
						ORDER BY v_idols.ordinal"""
		else:
			query = f"""SELECT * FROM v_idols
						ORDER BY v_idols.ordinal"""
					
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
			group_by = None, order_by = Ordinal, order = SortingOrder.Ascending,
			with_event_info = False, with_banner_info = False):
	
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
		
		database_view = 'v_idols_with_events'
		if with_event_info and with_banner_info:
			database_view = 'v_idols_with_event_info_and_banner_info_null_allowed'
		elif with_event_info:
			database_view = 'v_idols_with_event_info_null_allowed'
		elif with_banner_info:
			database_view = 'v_idols_with_banner_info_null_allowed'
		
		if fields:
			query = f"""SELECT * FROM '{database_view}'
						WHERE {' AND '.join([x[0] for x in fields])} {group_by}
						ORDER BY {order_by} {order}"""
			values = [value for x in fields for value in x[1]]
			self.db.execute(query, values)
		else:
			query = f"""SELECT * FROM '{database_view}'
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
	
	def get_newest_idols(self, group  : Union[Group, List[Group]]   = None, rarity  : Union[Rarity, List[Rarity]] = None,
							   source : Union[Source, List[Source]] = None, members : Union[Member, List[Member]] = None,
							   released_before : datetime = None):
		fields = []
		if group      != None: fields.append(self._make_where_condition("group_id",  group))
		if rarity     != None: fields.append(self._make_where_condition("rarity",    rarity))
		if source     != None: fields.append(self._make_where_condition("source",    source))
		if members    != None: fields.append(self._make_where_condition("member_id", members))
		
		if released_before != None:
			fields.append((f"release_date_jp <= ?", [released_before.isoformat()]))
		
		if fields:
			query = f"""SELECT * FROM 'v_idols_with_event_info_and_banner_info_null_allowed'
						WHERE ordinal IN (
							SELECT MAX(ordinal) FROM 'v_idols'
							WHERE {' AND '.join([x[0] for x in fields])}
							GROUP BY member_id
						)
						ORDER BY release_date_jp ASC"""
			# print(query)
			self.db.execute(query, [value for x in fields for value in x[1]])
		else:
			query = f"""SELECT * FROM 'v_idols_with_event_info_and_banner_info_null_allowed'
						WHERE ordinal IN (
							SELECT MAX(ordinal) FROM 'v_idols'
							GROUP BY member_id
						)
						ORDER BY release_date_jp ASC"""
			self.db.execute(query)
			
		return self.convert_to_idol_object(self.db.fetchall())
	
	# -------------------------------------------------------------------------------------------
	
	def get_general_stats(self):
		try:
			return self.general_stats, self.maximums
		except:
			self.general_stats = {}
			
		Stats = namedtuple('Stats', 'source rarity type attribute')
		
		def remove_default_factory(dd):
			dd.default_factory = None
			
		source_categories = {
			Source.Event       : 'event',
			Source.Festival    : 'festival',
			Source.Party       : 'party',
			Source.Gacha       : 'gacha',
			Source.Spotlight   : 'gacha',
			Source.Unspecified : 'gacha',
		}
		
		maximums = {
			Rarity.UR: 0,
			Rarity.SR: 0,
		}
		
		for group in Group:
			source_stats    = defaultdict(lambda: defaultdict(int))
			rarity_stats    = defaultdict(lambda: defaultdict(int))
			type_stats      = defaultdict(lambda: defaultdict(int))
			attribute_stats = defaultdict(lambda: defaultdict(int))
						
			idols = self.get_idols(group=group)
			for idol in idols:
				# Don't care about R cards
				if idol.rarity == Rarity.R: continue
				
				rarity_stats[idol.member_id][idol.rarity] += 1
				maximums[idol.rarity] = max(maximums[idol.rarity], rarity_stats[idol.member_id][idol.rarity])
				
				if idol.rarity == Rarity.UR:
					category = source_categories[idol.source]
					source_stats[idol.member_id][category] += 1
					
					attribute_stats[idol.member_id][idol.attribute] += 1
					type_stats[idol.member_id][idol.type] += 1
			
			remove_default_factory(source_stats)
			remove_default_factory(rarity_stats)
			remove_default_factory(type_stats)
			remove_default_factory(attribute_stats)
			
			self.general_stats[group] = Stats(
				source    = source_stats,
				rarity    = rarity_stats,
				type      = type_stats,
				attribute = attribute_stats,
			)
			self.maximums = maximums
			
		return self.general_stats, self.maximums
	
	# -------------------------------------------------------------------------------------------
	
	def get_banner_stats(self, banner_type : Union[BannerType, List[BannerType]], rarity : Union[Rarity, List[Rarity]]):
		fields = []
		fields.append(self._make_where_condition("b.type",   banner_type))
		fields.append(self._make_where_condition("i.rarity", rarity))
		
		query = f"""SELECT
						b.type,
						b.start_jp AS start,
						b.end_jp AS end,
						GROUP_CONCAT(c.ordinal) AS ordinals,
						GROUP_CONCAT(m.group_id) AS groups
					FROM banners b
						LEFT JOIN banner_cards c ON b.id = c.banner_id
						LEFT JOIN idols i ON c.ordinal = i.ordinal
						LEFT JOIN members m ON i.member_id = m.id
					WHERE {' AND '.join([x[0] for x in fields])}
					GROUP BY b.id
					ORDER BY start DESC
					LIMIT 10"""
		self.db.execute(query, [value for x in fields for value in x[1]])
		response_data = self.db.fetchall()
		
		most_recent_banner_type = BannerType(response_data[0]['type'])
		
		banners_by_type = defaultdict(list)
		for banner_data in response_data:
			idols  = self.get_idols_by_ordinal(banner_data['ordinals'].split(','))
			groups = [Group(int(x)) for x in banner_data['groups'].split(',')]
			
			banner_type = BannerType(banner_data['type'])
			banners_by_type[banner_type].append({
				'start'  : datetime.fromisoformat(banner_data['start']),
				'end'    : datetime.fromisoformat(banner_data['end']),
				'idols'  : idols,
				'groups' : groups,
			})
			
		banners_by_type.default_factory = None
		return most_recent_banner_type, banners_by_type
		
	# -------------------------------------------------------------------------------------------
	
	def get_weighted_overdueness(self, days_offset=0):
		overdue_sources = [Source.Festival, Source.Party]
		
		now = datetime.now(timezone.utc) + timedelta(days=days_offset)
		
		limited_idols, max_per_source = self.get_idols_by_source_and_member(overdue_sources)
		
		all_overdue_members = set()
		overdue_members = {}
		
		for member in Member:
			for source, data in limited_idols[member].items():
				if source not in overdue_members:
					overdue_members[source] = set()
					
				if data['num_idols'] < (max_per_source[source] + data['max_offset']):
					all_overdue_members.add(member)
					overdue_members[source].add(member)
					break
		
		# If nobody is overdue in current set then everyone is up for grabs
		for source in overdue_sources:
			if len(overdue_members[source]) == 0:
				overdue_members[source] = set([member for member in Member])
					
		max_UR_offsets = {
			Member.Rina     : -2,
			Member.Kasumi   : -2,
			Member.Shizuku  : -2,
			Member.Ayumu    : -2,
			Member.Setsuna  : -2,
			Member.Ai       : -2,
			Member.Emma     : -2,
			Member.Kanata   : -2,
			Member.Karin    : -2,
			Member.Shioriko : -3,
			Member.Lanzhu   : -7,
			Member.Mia      : -7,
		}
		
		general_stats, maximums = self.get_general_stats()
		expected_by_member = {}
		current_rotation_coefficient = {}
		for member in all_overdue_members:
			num_expected = maximums[Rarity.UR] + max_UR_offsets.get(member, 0)
			num_current  = general_stats[member.group].rarity[member][Rarity.UR]
			
			expected_by_member[member] = (num_current, num_expected)
			current_rotation_coefficient[member] = (num_expected / num_current)
		
		longest_overdue    = 0
		elapsed_per_member = {}
		all_urs            = self.get_newest_idols(rarity=Rarity.UR)
		for idol in all_urs:
			delta = now - idol.release_date[Locale.JP]
			longest_overdue = max(delta.days, longest_overdue)
			if idol.member_id in all_overdue_members:
				elapsed_per_member[idol.member_id] = delta
		
		banner_types = [x.banner_type for x in overdue_sources]
		most_recent_banner_type, banners_by_type = self.get_banner_stats(banner_type=banner_types, rarity=Rarity.UR)
		most_recent_groups = banners_by_type[most_recent_banner_type][0]['groups']
		# print(most_recent_banner_type, most_recent_groups)
		
		num_banners_for_group = defaultdict(lambda: defaultdict(int))
		elapsed_by_group = defaultdict(dict)
		for banner_type, banners in banners_by_type.items():
			num_banners_for_group[banner_type] = {
				'total'  : 0,
				'groups' : defaultdict(int)
			}
			
			for data in banners:
				for group in data['groups']:
					if group not in elapsed_by_group[banner_type]:
						elapsed_by_group[banner_type][group] = (now - data['start'])
						
					num_banners_for_group[banner_type]['total'] += 1
					num_banners_for_group[banner_type]['groups'][group] += 1
		
		elapsed_coefficients = {}
		for banner_type, data in elapsed_by_group.items():
			elapsed_coefficients[banner_type] = {group: 1 for group in Group}
			max_delta = max([delta for group, delta in data.items()])
			for group, delta in data.items():
				elapsed_coefficients[banner_type][group] = delta.days / max_delta.days
		
		banner_shares = {}
		for banner_type, data in num_banners_for_group.items():
			banner_shares[banner_type] = {group: 0 for group in Group}
			for group, value in data['groups'].items():
				banner_shares[banner_type][group] = value / data['total']
				
		def sigmoid(steepness, value):
			return 1 / (1 + math.e ** (-steepness * (value - 0.5)))
		
		# for banner_type, data in elapsed_by_group.items():
		# 	print(banner_type)
		# 	for group, delta in data.items():
		# 		num, total = num_banners_for_group[banner_type]['groups'][group], num_banners_for_group[banner_type]['total']
				
		# 		share = 1 / banner_shares[banner_type][group]
		# 		# share = sigmoid(8, share)
				
		# 		x = elapsed_coefficients[banner_type][group]
		# 		k = 8
		# 		ecff = sigmoid(k, x)
				
		# 		print(f"\t{group:>20}   {delta.days:>3} days ago  {num:>2}/{total:<2} ({share:.2f} share)  elapsed c. {x:0.2f} -> {ecff:0.2f}")
		
		# exit()
		
		other_banner_type = {
			BannerType.Festival : BannerType.Party,
			BannerType.Party    : BannerType.Festival,
		}
		next_banner_type = other_banner_type[most_recent_banner_type]
		
		weighted_overdueness = {}
		for current_source in overdue_sources:
			weighted_overdueness[current_source] = {}
			current_banner_type = current_source.banner_type
			
			found_members = set()
			limited_urs = self.get_newest_idols(rarity=Rarity.UR, source=overdue_sources)
			for idol in limited_urs:
				if idol.member_id not in overdue_members[current_source]:
					continue
				
				member = idol.member_id
				found_members.add(member)
				
				ur_coefficient = elapsed_per_member[member].days / longest_overdue
				limited_delta = now - idol.release_date[Locale.JP]
				
				banner_share = banner_shares[current_banner_type][member.group]
				banner_share = (1 / banner_share) if banner_share > 0 else 10
				
				sigmoid_steepness = 8
				banner_elapsed_coefficient = elapsed_coefficients[current_banner_type][member.group]
				banner_elapsed_coefficient = sigmoid(sigmoid_steepness, banner_elapsed_coefficient)
				
				weighted_value = ur_coefficient * limited_delta.days
				weighted_value *= banner_share
				weighted_value *= banner_elapsed_coefficient
				
				if next_banner_type == current_banner_type:
					if member.group in most_recent_groups:
						weighted_value *= 0.85
					else:
						weighted_value *= 1.15
						
				if weighted_value > 0:	
					weighted_value **= current_rotation_coefficient.get(member, 1)
				
				weighted_overdueness[current_source][member] = {
					'last_any_ur'       : elapsed_per_member[member],
					'last_limited_ur'   : limited_delta,
					'weighted_value'    : weighted_value,
					'num_urs'           : expected_by_member[member],
					'last_limited_card' : idol,
				}
			
			for member in overdue_members[current_source]:
				if member in found_members:
					continue
					
				ur_coefficient = elapsed_per_member[member].days / longest_overdue
				release_delta = now - self.member_addition_dates[member]['date_added']
				
				banner_share = banner_shares[current_banner_type][member.group]
				banner_share = (1 / banner_share) if banner_share > 0 else 10
				
				sigmoid_steepness = 8
				banner_elapsed_coefficient = elapsed_coefficients[current_banner_type][member.group]
				banner_elapsed_coefficient = sigmoid(sigmoid_steepness, banner_elapsed_coefficient)
				
				weighted_value = ur_coefficient * release_delta.days
				weighted_value *= banner_share
				weighted_value *= banner_elapsed_coefficient
				
				if next_banner_type == current_banner_type:
					if member.group in most_recent_groups:
						weighted_value *= 0.75
					else:
						weighted_value *= 1.25
						
				if weighted_value > 0:	
					weighted_value **= current_rotation_coefficient.get(member, 1)
				
				weighted_overdueness[current_source][member] = {
					'last_any_ur'       : elapsed_per_member[member],
					'last_limited_ur'   : None,
					'weighted_value'    : weighted_value,
					'num_urs'           : expected_by_member[member],
					'last_limited_card' : None,
				}
			
			weighted_overdueness[current_source] = {k: v for k, v in sorted(weighted_overdueness[current_source].items(), key=lambda x: x[1]['weighted_value'], reverse=True)}
				
		return weighted_overdueness
		
	# -------------------------------------------------------------------------------------------
	
	def get_member_addition_dates(self):
		return self.member_addition_dates
	
	def _initialize_member_addition_dates(self):
		try:
			if self.member_addition_dates: return
		except AttributeError:
			pass
			
		member_release_date = {
			Locale.JP : {
				Member.Shioriko : datetime(2020, 8, 5, 6, 0, tzinfo=timezone.utc),
				Member.Lanzhu   : datetime(2021, 9, 3, 6, 0, tzinfo=timezone.utc),
				Member.Mia      : datetime(2021, 9, 3, 6, 0, tzinfo=timezone.utc),
			},
			Locale.WW : {
				Member.Shioriko : datetime(2020, 11, 21, 6, 0, tzinfo=timezone.utc),
				Member.Lanzhu   : datetime(2021, 9,  3,  6, 0, tzinfo=timezone.utc),
				Member.Mia      : datetime(2021, 9,  3,  6, 0, tzinfo=timezone.utc),
			},
		}
		
		sifas_launch_date = {
			Locale.JP : datetime(2019, 9, 26, 15, 0, tzinfo=timezone.utc),
			Locale.WW : datetime(2020, 2, 25, 15, 0, tzinfo=timezone.utc),
		}
		
		self.member_addition_dates = {locale: {} for locale in Locale}
		for locale in Locale:
			for member in Member:
				date_added = member_release_date[locale].get(member, sifas_launch_date[locale])
				game_launch = ((sifas_launch_date[locale] - date_added).days == 0)
				
				self.member_addition_dates[locale][member] = {
					'date_added'  : date_added,
					'game_launch' : game_launch,
				}
	
	# -------------------------------------------------------------------------------------------
	
	# Categories should be a dictionary of tuples with "category name" as the key
	# and value being ([list of rarities], [list of sources]) or None instead of list for any.
	def get_idol_history(self, member : Member, categories, time_now : datetime):
		assert(member != None and isinstance(member, Member))
		
		fields = []
		fields.append(self._make_where_condition("member_id", member))
		
		query = f"""SELECT * FROM v_idols_with_event_info_and_banner_info_null_allowed
					WHERE {' AND '.join([x[0] for x in fields])}
					ORDER BY release_date_jp ASC"""
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
				
				time_since_release = {locale: time_now - idol.release_date[locale] for locale in Locale}
				if previous_idol:
					time_since_previous = {locale: idol.release_date[locale] - previous_idol.release_date[locale] for locale in Locale}
				else:
					time_since_previous = {locale: idol.release_date[locale] - self.member_addition_dates[locale][member]['date_added'] for locale in Locale}
				
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
					'start' : {
						Locale.JP : datetime.fromisoformat(data['event_start_jp']),
						Locale.WW : datetime.fromisoformat(data['event_start_ww']),
					},
					'end'   : {
						Locale.JP : datetime.fromisoformat(data['event_end_jp']),
						Locale.WW : datetime.fromisoformat(data['event_end_ww']),
					},
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
				   LEFT JOIN idols       ON idols.member_id = members.id AND idols.source = ? AND idols.rarity = ?
				   LEFT JOIN event_cards ON idols.ordinal   = event_cards.ordinal
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
					# 'title' : data['banner_title_ww'],
					'type'  : BannerType(data['banner_type']),
					'start' : {
						Locale.JP : datetime.fromisoformat(data['banner_start_jp']),
						Locale.WW : datetime.fromisoformat(data['banner_start_ww']),
					},
					'end'   : {
						Locale.JP : datetime.fromisoformat(data['banner_end_jp']),
						Locale.WW : datetime.fromisoformat(data['banner_end_ww']),
					},
				}
			
			card = KiraraIdol(self, data)
			
			banners[banner_id]['cards'].append(card)
			banners[banner_id]['cards'].sort(key=lambda x: (-x.rarity.value, x.ordinal))
			
			banners[banner_id]['num_others'] = data['banner_num_cards'] - len(banners[banner_id]['cards'])
			
			if card.rarity == Rarity.UR:
				index = self._get_card_member_index(card.ordinal)
				banners[banner_id]['index'] = max(banners[banner_id]['index'], index)
			
		return banners
		
	def get_idols_by_source_and_member(self, sources : List[Source] = [], rarity : Rarity = Rarity.UR,
		                                     released_before : Optional[datetime] = None):
		if not sources: raise KiraraClientValueError("Sources empty.")
		
		if released_before != None:
			released_before = f"AND release_date_jp <= '{released_before.isoformat()}'"
		else:
			released_before = ""
		
		query = f"""SELECT member_id, COUNT(ordinal) AS num_idols, GROUP_CONCAT(ordinal) AS idol_ordinals
					FROM idols i
					WHERE source = ? AND rarity = ? {released_before}
					GROUP BY member_id"""
		
		max_offsets_per_member = {
			Member.Mia    : { Source.Festival : -2, Source.Party : 0, },
			Member.Lanzhu : { Source.Festival : -2, Source.Party : 0, },
		}
		
		max_per_source = dict()
		num_idols_by_member = defaultdict(dict)
		for source in sources:
			max_per_source[source] = 0
			
			for member in Member:
				try:
					max_offset = max_offsets_per_member[member][source]
				except:
					max_offset = 0
					
				num_idols_by_member[member][source] = {
					'num_idols'  : 0,
					'idols'      : [],
					'max_offset' : max_offset,
				}
			
			self.db.execute(query, [source.value, rarity.value])
			for row in self.db.fetchall():
				member = Member(row['member_id'])
				num_idols_by_member[member][source]['num_idols'] = row['num_idols']
				
				max_per_source[source] = max(row['num_idols'], max_per_source[source])
				
		return num_idols_by_member, max_per_source
		
	# -------------------------------------------------------------------------------------------
		
	def convert_to_idol_object(self, data):
		return [KiraraIdol(self, x) for x in data]
	
	# -------------------------------------------------------------------------------------------
	
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
	
	
			

if __name__ == "__main__":
	client = KiraraClient()
	client.cache_all_idols()
	exit()
	
