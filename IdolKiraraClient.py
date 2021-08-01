import requests
import json
import sqlite3 as sqlite
from IdolDatabase import *
from operator import itemgetter
import time

def chunked(seq, size):
	for x in range(0, len(seq), size):
		yield seq[x:x+size]

class KiraraClientException(Exception): pass
class KiraraClientValueError(KiraraClientException): pass

class KiraraIdol():
	def __init__(self, data):
		self.ordinal   = data['ordinal']
		self.id        = data['id']
		self.member_id = data['member_id']
		self.type      = data['type']
		self.attribute = data['attribute']
		self.rarity    = data['rarity']
		self.data = json.loads(data['json'])
	
	def __str__(self):
		idol = Idols.ByMemberId[self.member_id]
		return f"{self.get_name(True)} {Attribute(self.attribute).name} {Type(self.type).name} {idol}"
	
	def __repr__(self):
		idol = Idols.ByMemberId[self.member_id]
		return f"{self.get_name(True)} {Attribute(self.attribute).name} {Type(self.type).name} {idol}"
	
	def get_name(self, idolized : bool):
		if idolized:
			return self.data['idolized_appearance']['name']
		
		return self.data['normal_appearance']['name']
	
	def get_parameters(self, level : int, limit_break : int):
		if not (level >= 1 and level <= 100):
			raise KiraraClientValueError("Level must be between 1-100.")
			
		if not (limit_break >= 0 and limit_break <= 5):
			raise KiraraClientValueError("Limit break must be between 0-5")
		
		return (
			self.data["stats"][level - 1][1] + self.data["tt_offset"][limit_break][1] + self.data["idolized_offset"][1],
			self.data["stats"][level - 1][2] + self.data["tt_offset"][limit_break][2] + self.data["idolized_offset"][2],
			self.data["stats"][level - 1][3] + self.data["tt_offset"][limit_break][3] + self.data["idolized_offset"][3],
		)

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
		self.dbcon = sqlite.connect(KiraraClient.DatabaseFile)
		self.dbcon.row_factory = sqlite.Row
		self.db = self.dbcon.cursor()
				
		db_schema = '''CREATE TABLE `idols` (
		               `ordinal`    INTEGER UNIQUE,
		               `id`         INTEGER UNIQUE,
		               `member_id`  INTEGER,
		               `attribute`  INTEGER,
		               `type`       INTEGER,
		               `rarity`     INTEGER,
		               `json`       TEXT,
		               PRIMARY KEY(`ordinal`, `id`)
		            )'''
		
		try:
			self.db.execute(db_schema)
			self.dbcon.commit()
		except sqlite.OperationalError:
			pass
	
	def cache_all_idols(self):
		url = KiraraClient.Endpoints['id_list']
		print(url)
		r = requests.get(url)
		if r.status_code != 200:
			raise KiraraClientException("Endpoint status not OK")
		
		data = r.json()
		existing_ordinals = set([x[0] for x in self.db.execute("SELECT ordinal FROM `idols`")])
		
		ordinals = []
		for card in data['result']:
			if card['ordinal'] not in existing_ordinals:
				ordinals.append(card['ordinal'])
		
		for x in chunked(ordinals, 10):
			print(x)
			self.get_idols_by_ordinal(x)
		
	def get_idols_by_ordinal(self, ordinals):
		assert isinstance(ordinals, int) or isinstance(ordinals, list)
		
		if isinstance(ordinals, int):
			ordinals = set([ordinals])
		elif isinstance(ordinals, list):
			ordinals = set(ordinals)
			
		result = []
		
		# Check for cards in cache database
		query = "SELECT * FROM `idols` WHERE {}".format(' OR '.join(["`ordinal` = ?"] * len(ordinals)))
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
			if r.status_code != 200:
				raise KiraraClientException("Endpoint status not OK")
			
			data = r.json()
			num_results = len(data['result'])
			
			query_data = []
			for card in data['result']:
				d = (
					card['ordinal'],
					card['id'],
					card['member'],
					card['attribute'],
					card['role'],
					card['rarity'],
					json.dumps(card),
				)
				query_data.append(d)
				
			query_data = list(sorted(query_data, key=itemgetter(0)))
			query = "INSERT INTO `idols` (`ordinal`, `id`, `member_id`, `attribute`, `type`, `rarity`, `json`) VALUES (?, ?, ?, ?, ?, ?, ?)"
			self.db.executemany(query, query_data)
			self.dbcon.commit()
			
			result.extend(query_data)
		
		return [KiraraIdol(x) for x in result]
		

client = KiraraClient()
# client.cache_all_idols()

# data = client.get_idols_by_ordinal([1, 2, 345, 466, 491, 311])

data = client.get_idols_by_ordinal(373)[0]
print(data)
params = data.get_parameters(82, 5)
print(params)

