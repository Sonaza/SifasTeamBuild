import os
import math
from datetime import datetime, timezone
from IdolDatabase import *
from CardValidity import *

from jinja2 import Environment, PackageLoader, FileSystemLoader, select_autoescape
import htmlmin

def _ordinalize(n):
	n = int(n)
	if 11 <= (n % 100) <= 13:
		suffix = 'th'
	else:
		suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
	return str(n) + suffix
	
def _pluralize(value, singular, plural):
	if abs(value) == 1:
		return f"{abs(value)} {singular}"
	else:
		return f"{abs(value)} {plural}"

def _format_days(value):
	if value > 0:
		return f"{_pluralize(value, 'day', 'days')} ago"
	elif value == 0:
		return "Today"
	else:
		return f"In {_pluralize(value, 'day', 'days')}"

def _format_years_days(value):
	years = math.floor(value / 365)
	
	if value > 0:
		if years > 0:
			return f"{years} y {value % 365} d ago"
		else:
			return f"{_pluralize(value, 'day', 'days')} ago"
	elif value == 0:
		return "Today"
	else:
		return f"In {_pluralize(value, 'day', 'days')}"

def _format_delta_days(value):
	if value > 0:
		return f"{_pluralize(value, 'day', 'days')}"
	elif value == 0:
		return "0 days"
	else:
		return "Negative days impossible"
	
def _conditional_css(class_names, condition):
	assert isinstance(class_names, str) or isinstance(class_names, list) or isinstance(class_names, tuple)
	assert isinstance(condition, bool)
	
	if isinstance(class_names, str): class_names = [class_names, '']
	elif len(class_names) == 1:      class_names = [class_names[0], '']
		
	if condition:
		return class_names[0]
	else:
		return class_names[1]

def get_file_modifyhash(filepath):
	modify_time = os.stat(filepath).st_mtime
	hashvalue = hash(modify_time) % 16711425
	return f"{hashvalue:06x}"

def _cache_buster(output_directory, filename):
	full_path = os.path.normpath(output_directory + '/' + filename)
	if not os.path.exists(full_path):
		print(f"Cache busting path {full_path} does not exist!")
		return filename
		
	name, ext = os.path.splitext(filename)
	buster = get_file_modifyhash(full_path)
	return f"{name}.{buster}{ext}"
	
def _include_page(filepath, minify=False):
	if not os.path.exists(filepath):
		return f"<h1>Error: {filepath} does not exist.</h1>"
	
	with open(filepath, encoding="utf8") as f:
		data = f.read()
		if minify:
			data = htmlmin.minify(data, remove_empty_space=True)
		return data
		
	return f"<h1>Error: Failed to open {filepath}.</h1>"
	
def _get_card_source_label(card):
	if card.source == Source.Gacha:
		if card.event_title != None:
			return 'Event Gacha'
		
	return card.source.display_name
		
# -------------------------------------------------------------------------------------------

class PageRenderer():
	RENDER_HISTORY_FILE = "render_history.json"
	
	def __init__(self, parent):
		self.parent = parent
		
		self.jinja = Environment(
			# loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__)), encoding='utf-8'),
			loader=PackageLoader("CardRotations", encoding='utf-8'),
			# autoescape=select_autoescape()
		)
		
		self.jinja.filters.update({
			'format_days'       : _format_days,
			'format_years_days' : _format_years_days,
			'format_delta_days' : _format_delta_days,
			'pluralize'         : _pluralize,
			'ordinalize'        : _ordinalize,
			
			'conditional_css'   : _conditional_css,
		})
		
		self.jinja.globals.update({
			# Python built in functions
			'reversed'              : reversed,
			'len'                   : len,
			
			# Application related variables
			'cmd_args'              : self.parent.args,
			
			# Application related global enums
			'Idols'                 : Idols,
			'Member'                : Member,
			'Group'                 : Group,
			'Rarity'                : Rarity,
			'Source'                : Source,
			'Attribute'             : Attribute.get_valid(),
			'Type'                  : Type.get_valid(),
			
			'BannerType'            : BannerType.get_valid(),
			
			# Page specific functions
			'is_valid_card'         : is_valid_card,
			'is_missing_card'       : is_missing_card,
			'is_nonextant_card'     : is_nonextant_card,
			
			'include_page'          : _include_page,
			
			# Systems stuff
			'cache_buster'          : lambda filepath: _cache_buster(self.parent.OutputDirectory, filepath),
			
			'get_card_source_label' : _get_card_source_label,
		})
		
		self.rendered_pages = []
		
		self.load_render_history()
		
	# -------------------------------------------------------------------------------------------
	
	def reset_render_history(self):
		self.render_history = {}
		
	def load_render_history(self):
		self.render_history = {}
		if os.path.exists(PageRenderer.RENDER_HISTORY_FILE):
			try:
				with open(PageRenderer.RENDER_HISTORY_FILE, "r") as f:
					self.render_history = json.load(f)
				
				for template, data in self.render_history.items():
					data['last_used'] = datetime.fromisoformat(data['last_used'])
			except:
				self.render_history = {}
		
	def save_render_history(self):
		if not isinstance(self.render_history, dict):
			return False
			
		def json_serialize(obj):
		    if isinstance(obj, (datetime)):
		        return obj.isoformat()
		    raise TypeError(f"Type {type(obj)} not serializable")
		
		with open(PageRenderer.RENDER_HISTORY_FILE, "w") as f:
			json.dump(self.render_history, f, default=json_serialize)
		
		return True
	
	def has_template_changed(self, template_filename):
		if template_filename not in self.render_history:
			return True
		if 'last_used' not in self.render_history[template_filename]:
			return True
		
		template_filename_path = os.path.join("templates", template_filename)
		file_modified_time = datetime.utcfromtimestamp(os.path.getmtime(template_filename_path)).replace(tzinfo=timezone.utc)
		
		if self.render_history[template_filename]['last_used'] < file_modified_time:
			return True
		
		return False
		
	def is_any_output_missing(self, template_filename):
		if template_filename not in self.render_history:
			return True
		if 'output' not in self.render_history[template_filename]:
			return True
		if len(self.render_history[template_filename]['output']) == 0:
			return True
			
		for output_filename in self.render_history[template_filename]['output']:
			if not os.path.exists(output_filename):
				return True
				
		return False
	
	def reset_output(self, template_filename):
		if template_filename not in self.render_history:
			return False
			
		self.render_history[template_filename]['output'] = []
	
	def preserve_output(self, template_filename):
		if template_filename not in self.render_history:
			return False
		if 'output' not in self.render_history[template_filename]:
			return False
		
		self.rendered_pages.extend(self.render_history[template_filename]['output'])
	
	# -------------------------------------------------------------------------------------------
		
	def render_and_save(self, template_filename, output_filename, data, minify=True, output_basepath=None, generated_note=False):
		if template_filename not in self.render_history:
			self.render_history[template_filename] = {
				'last_used' : None,
				'output'    : [],
			}
			
		if output_basepath == None:
			output_basepath = self.parent.OutputDirectory
		
		output_filename = os.path.normpath(os.path.join(output_basepath, output_filename)).replace("\\", "/")
		print(f"{f'Rendering  {template_filename:<30}  ->  {output_filename}':<90} ...  ", end='')
		
		self.render_history[template_filename]['last_used'] = datetime.now(timezone.utc)
		self.render_history[template_filename]['output'].append(output_filename)
		
		# template = self.jinja.get_template(os.path.join("templates", template_filename).replace("\\","/"))
		template = self.jinja.get_template(template_filename)
		rendered_output = template.render(data)
		
		if minify:
			rendered_output = htmlmin.minify(rendered_output, remove_empty_space=True)
		
		with open(output_filename, "w", encoding="utf8") as f:
			if generated_note:
				f.write(f"# ------------------------------------------------------------\n")
				f.write(f"# DO NOT MODIFY THIS FILE DIRECTLY\n")
				f.write(f"# This file was auto generated from {template_filename}\n")
				f.write(f"# ------------------------------------------------------------\n")
			f.write(rendered_output)
			f.close()
		
		print("Done")
		
		self.rendered_pages.append(output_filename)
		return output_filename
