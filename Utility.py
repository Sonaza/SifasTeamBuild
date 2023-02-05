import os
import platform
import htmlmin
import json
import base64
from datetime import datetime, timezone
from IdolDatabase import *

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
	def conditional_css(class_names, condition):
		assert isinstance(class_names, str) or isinstance(class_names, list) or isinstance(class_names, tuple)
		assert isinstance(condition, bool)
		
		if isinstance(class_names, str): class_names = [class_names, '']
		elif len(class_names) == 1:      class_names = [class_names[0], '']
			
		if condition:
			return class_names[0]
		else:
			return class_names[1]

	@staticmethod
	def get_file_modifyhash(filepath):
		modify_time = os.stat(filepath).st_mtime
		hashvalue = hash(modify_time) % 16711425
		return f"{hashvalue:06x}"

	@staticmethod
	def cache_buster(root_directory, filepath):
		full_filepath = os.path.normpath(root_directory + '/' + filepath).replace("\\", "/")
		if not os.path.exists(full_filepath):
			print(f"Cache busting path {full_filepath} does not exist!")
			return filepath
			
		name, ext = os.path.splitext(filepath)
		buster = Utility.get_file_modifyhash(full_filepath)
		return f"{name}.{buster}{ext}"
		
	@staticmethod
	def include_static(filename, minify=False, root_directory="templates"):
		full_filepath = os.path.join(root_directory, filename).replace("\\", "/")
		if not os.path.exists(full_filepath):
			return f"<h1>Error: {full_filepath} does not exist.</h1>"
		
		with open(full_filepath, encoding="utf8") as f:
			data = f.read()
			if minify:
				data = htmlmin.minify(data, remove_empty_space=True)
			return data
			
		return f"<h1>Error: Failed to open {full_filepath}.</h1>"
		
	@staticmethod
	def get_card_source_label(card):
		if card.source == Source.Gacha:
			if card.event_title != None:
				return 'Event Gacha'
		return card.source.display_name

	@staticmethod
	def is_windows():
		return (platform.system() == "Windows" or 'CYGWIN_NT' in platform.system())

	@staticmethod
	def format_datestring(date, long_month = False, ordinalize = True, with_utc_time = False):
		day_format   = '%#d' if Utility.is_windows() else '%-d'
		month_format = '%B' if long_month else '%b'
		
		format_string = f'{day_format} {month_format} %Y'
		if with_utc_time:
			format_string = f'{format_string} %H:%M %Z'
		
		day, month, year = date.strftime(format_string).split(' ', 2)
		
		if ordinalize:
			day = f"{Utility.ordinalize(day)} of"
		
		return f"{day} {month} {year}"
	
	# ----------------------------------------------------------
		
	@staticmethod
	def serialize_card(card):
		data = {
			'm' : [ card.member_id.value, card.member_id.full_name ],
			'd' : [ card.ordinal, card.rarity.value, card.attribute.value, card.type.value ],
			't' : [ card.get_card_name(False), card.get_card_name(True) ],
			's' : Utility.get_card_source_label(card),
			'r' : [ Utility.format_datestring(card.release_date[Locale.JP], long_month=True) ],
		}
		
		if card.release_date[Locale.JP] != card.release_date[Locale.WW]:
			data['r'].append(Utility.format_datestring(card.release_date[Locale.WW], long_month=True))
		
		if card.event_title:
			data['e'] = card.event_title
			
		return data
	
	@staticmethod
	def serialize_member(member):
		data = {
			'm' : [ member.value, member.full_name ],
		}
		return data
	
	@staticmethod
	def base64encode_json(data):
		serialized = json.dumps(data, separators=(',', ':'))
		return base64.b64encode(serialized.encode('utf-8')).decode('utf-8')
		
	@staticmethod
	def card_to_base64(card):
		return Utility.base64encode_json(Utility.serialize_card(card))
		
	@staticmethod
	def member_to_base64(member):
		return Utility.base64encode_json(Utility.serialize_member(card))
		
		
if __name__ == "__main__":
	print(Utility.get_method_list())
