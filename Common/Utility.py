import os
import platform
import htmlmin
import json
import base64
import math
from glob import glob
from datetime import datetime, timedelta, timezone

from typing import List, Optional, Tuple, Dict, Any, Union

class Utility:
	@classmethod
	def get_method_list(cls):
		return {method_name: method for method_name, method in cls.__dict__.items() if isinstance(method, staticmethod)}
		
		
	@staticmethod
	def ordinalize(n):
		n = int(n)
		if 11 <= (n % 100) <= 13:
			suffix = 'th'
		else:
			suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
		return str(n) + suffix
		
		
	@staticmethod
	def pluralize(value, singular, plural):
		if abs(value) == 1:
			return f"{abs(value)} {singular}"
		else:
			return f"{abs(value)} {plural}"
	
	# ----------------------------------------------------------

	@staticmethod
	def is_windows():
		return (platform.system() == "Windows" or 'CYGWIN_NT' in platform.system())
	
	# ----------------------------------------------------------
		
	@staticmethod
	def format_days(value):
		if value > 0:
			return f"{Utility.pluralize(value, 'day', 'days')} ago"
		elif value == 0:
			return "Today"
		else:
			return f"In {Utility.pluralize(value, 'day', 'days')}"


	@staticmethod
	def format_years_days(value):
		years = math.floor(value / 365)
		
		if value > 0:
			if years > 0:
				return f"{years} y {value % 365} d ago"
			else:
				return f"{Utility.pluralize(value, 'day', 'days')} ago"
		elif value == 0:
			return "Today"
		else:
			return f"In {Utility.pluralize(value, 'day', 'days')}"


	@staticmethod
	def format_delta_days(value):
		if value > 0:
			return f"{Utility.pluralize(value, 'day', 'days')}"
		elif value == 0:
			return "0 days"
		else:
			return "Negative days impossible"


	@staticmethod
	def format_datestring(date, with_day = True, ordinalize = True, long_month = False, with_year = True, with_utc_time = False):
		day_format      = '%#d' if Utility.is_windows() else '%-d'
		month_format    = '%B' if long_month else '%b'
		year_format     = '%Y'
		utc_time_format = '%H:%M %Z'
		
		date_format_segments = []
		
		if with_day:
			date_format_segments.append(day_format)
		
		date_format_segments.append(month_format)
		
		if with_year:     date_format_segments.append(year_format)
		if with_utc_time: date_format_segments.append(utc_time_format)
		
		date_formatted = [date.strftime(format_string) for format_string in date_format_segments]
		if with_day and ordinalize:
			date_formatted[0] = Utility.ordinalize(date_formatted[0])
		
		return Utility.concat(date_formatted, separator=' ')
	
	# ----------------------------------------------------------
		
	@staticmethod
	def conditional(strings, condition):
		assert isinstance(strings, str) or isinstance(strings, list) or isinstance(strings, tuple)
		assert isinstance(condition, bool)
		return Utility.concat(strings, separator=' ') if condition else ''
	
	# ----------------------------------------------------------
	
	@staticmethod
	def concat(iterable, separator=',', last_separator=None):
		if isinstance(iterable, str):
			return iterable
		if last_separator == None:
			return str(separator).join([str(x) for x in iterable])
		else:
			return str(last_separator).join(str(separator).join([str(x) for x in iterable]).rsplit(separator, 1))
	
	@staticmethod
	def concat_with_format(format_info, iterable, *args, **kwargs):
		format_key, format_string = format_info
		formatted = [format_string.format(**{format_key: value}) for value in iterable]
		return Utility.concat(formatted, *args, **kwargs)
	
	# ----------------------------------------------------------
	
	@staticmethod
	def getter(data: Dict[str, Any], key: str, default: Any, wrapper: Optional = None):
		if key in data.keys() and data[key] != None:
			return wrapper(data[key]) if wrapper != None else data[key]
		return default
		
		
	@staticmethod
	def sort_by_key_order(data, key_order):
		return [(key, data[key]) for key in key_order if key in data]
		
		
	@staticmethod
	def swap_keys_and_values(dictionary):
		return {v: k for k, v in dictionary.items()}
	
	
	@staticmethod
	def join_path(*args, normalize=False):
		output = os.path.join(*args)
		if normalize: output = os.path.normpath(output)
		return output.replace('\\', '/')
	
	# ----------------------------------------------------------
	
	@staticmethod
	def contains_all(container, items):
		for value in items:
			if value not in container: return False
		return True
	
	
	@staticmethod
	def contains_none(container, items):
		for value in items:
			if value in container: return False
		return True
	
	
	@staticmethod
	def contains_one(container, items):
		for value in items:
			if value in container: return True
		return False
	
	# ----------------------------------------------------------
	
	@staticmethod
	def list_range(start, number_of_entries_inclusive):
		return list(range(start, start + number_of_entries_inclusive))
	
	@staticmethod
	def tuple_range(start, number_of_entries_inclusive):
		return tuple(range(start, start + number_of_entries_inclusive))
	
	# ---------------------------------------------------------
	
	@staticmethod
	def glob(globs_list : Union[str, List], recursive=False):
		if isinstance(globs_list, str): globs_list = [globs_list]
		output_paths = []
		for glob_path in globs_list:
			output_paths.extend([x.replace("\\", "/") for x in glob(glob_path, recursive=recursive)])
		return output_paths
		
	
	@staticmethod
	def read_file(full_filepath):
		try:
			with open(full_filepath, "r", encoding="utf8") as input_file:
				return input_file.read()
		except:
			return False
	
	
	@staticmethod
	def get_file_modify_utcdate(file_path):
		return datetime.utcfromtimestamp(os.path.getmtime(file_path)).replace(tzinfo=timezone.utc)
	

	@staticmethod
	def get_file_modify_hash(file_path):
		hashvalue = hash(os.path.getmtime(file_path)) % 16711425
		return f"{hashvalue:06x}"
		

	@staticmethod
	def cache_buster(root_directory, filepath):
		full_filepath = os.path.normpath(root_directory + '/' + filepath).replace("\\", "/")
		if not os.path.exists(full_filepath):
			print(f"Cache busting path {full_filepath} does not exist!")
			return filepath
			
		name, ext = os.path.splitext(filepath)
		buster = Utility.get_file_modify_hash(full_filepath)
		return f"{name}.{buster}{ext}"
	
	# ----------------------------------------------------------
	
	@staticmethod
	def timedelta_float(delta: timedelta, unit: str):
		return delta / timedelta(**{ unit: 1 })
		
	@staticmethod
	def wrap_year_and_month(year: int, month: int):
		if month > 12:
			return year + 1, 1
		return year, month
	
	# ----------------------------------------------------------
	
	@staticmethod
	def dbgprint(kw=None, *args, **kwargs):
		if kw != None:
			for key, value in kw.items():
				kwargs[key] = value
		
		longest_key      = max([4] + [len(str(key)) + 3 for key in kwargs.keys()])
		longest_typeinfo = max(
			[10] +
			[len(f"({type(value).__name__})") for value in args] +
			[len(f"({type(value).__name__})") for value in kwargs.values()]
		)
		
		for index, value in enumerate(args):
			tag = f"P[{index}]"
			type_info = f"({type(value).__name__})"
			print(f"{tag:<{longest_key}} {type_info:>{longest_typeinfo}} =  ", end='')
			if isinstance(value, str):
				print(f'"{value}"')
			else:
				print(value)
		
		for key, value in kwargs.items():
			tag = f"K[{key}]"
			type_info = f"({type(value).__name__})"
			print(f"{tag:<{longest_key}} {type_info:>{longest_typeinfo}} =  ", end='')
			if isinstance(value, str):
				print(f'"{value}"')
			else:
				print(value)

import builtins
builtins.dbgprint = Utility.dbgprint
