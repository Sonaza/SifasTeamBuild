
from enum import Enum
from typing import List, Optional, Tuple, Dict, Any, Union
import sqlite3 as sqlite
from Common import Utility

try:
	from collections.abc import KeysView
except:
	from collections import KeysView

class DBUtilityValueError(Exception): pass

class Row(sqlite.Row):
	def __getattr__(self, attr):
		return super().__getitem__(attr)
	
	def __repr__(self):
		return str(dict(self))

class InsertType(Enum):
	Normal = 0
	Ignore = 1
	Update = 2
	
def table_columns(db, table_name):
	db.execute(f"PRAGMA table_info('{table_name}')")
	return [column['name'] for column in db.fetchall()]
	
def table_exists(db, table_name):
	db.execute(f"PRAGMA table_info('{table_name}')")
	print(db.rowcount, list(db.fetchall()))
	return db.rowcount > 0

def make_insert_query(table : str, columns : list, insert_type : InsertType = InsertType.Normal):
	if len(table) == 0: raise DBUtilityValueError("Table must be set.")
	if len(columns) == 0:  raise DBUtilityValueError("Columns must be set.")
	if isinstance(columns, dict): columns = list(columns.keys())
	if isinstance(columns, KeysView): columns = list(columns)
	
	columns_concat = Utility.concat(columns, ', ')
	placeholders = Utility.concat_with_format(('v', ":{v}"), columns, separator=', ')
	
	if insert_type == InsertType.Normal:
		return f"""INSERT INTO {table} ({columns_concat}) VALUES ({placeholders})"""
		
	if insert_type == InsertType.Ignore:
		return f"""INSERT OR IGNORE INTO {table} ({columns_concat}) VALUES ({placeholders})"""
	
	if insert_type == InsertType.Update:
		primary_key = columns[0]
		updates = Utility.concat([f"{key}=:{key}" for key in columns], ', ')
		return f"""INSERT INTO {table} ({columns_concat}) VALUES ({placeholders})
		           ON CONFLICT({primary_key}) DO UPDATE SET {updates}"""
	
	raise DBUtilityValueError("Insert type is invalid.")
	
def get_enum_values(enum_list):
	return [enum.value for enum in enum_list]

def where_placeholders(data):
	return Utility.concat(['?'] * len(data))

