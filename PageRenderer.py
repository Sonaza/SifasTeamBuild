import os
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
	
def _conditional_css(class_names, condition):
	assert isinstance(class_names, str) or isinstance(class_names, list) or isinstance(class_names, tuple)
	assert isinstance(condition, bool)
	
	if isinstance(class_names, str): class_names = [class_names, '']
	elif len(class_names) == 1:      class_names = [class_names[0], '']
		
	if condition:
		return class_names[0]
	else:
		return class_names[1]
		
def _cache_buster(output_directory, filename):
	full_path = os.path.normpath(output_directory + '/' + filename)
	if not os.path.exists(full_path):
		print(f"Cache busting path {full_path} does not exist!")
		return filename
		
	modify_time = os.stat(full_path).st_mtime
	name, ext = os.path.splitext(filename)
	hashvalue = hash(modify_time) % 16711425
	return f"{name}.{hashvalue:06x}{ext}"
	
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
	def __init__(self, parent):
		self.parent = parent
		
		self.jinja = Environment(
			# loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__)), encoding='utf-8'),
			loader=PackageLoader("CardRotations", encoding='utf-8'),
			# autoescape=select_autoescape()
		)
		
		self.jinja.filters.update({
			'format_days'     : _format_days,
			'pluralize'       : _pluralize,
			'ordinalize'      : _ordinalize,
			
			'conditional_css' : _conditional_css,
		})
		
		self.jinja.globals.update({
			# Python built in functions
			'reversed'              : reversed,
			
			# Application related variables
			'cmd_args'              : self.parent.args,
			
			# Application related global enums
			'Idols'                 : Idols,
			'Member'                : Member,
			'Groups'                : Group,
			'Attribute'             : Attribute.get_valid(),
			'Type'                  : Type.get_valid(),
			
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
		
	# -------------------------------------------------------------------------------------------
		
	def render_and_save(self, template_filename, output_filename, data, minify=True, output_basepath=None):
		if output_basepath == None:
			output_basepath = self.parent.OutputDirectory
		
		output_filename = os.path.normpath(os.path.join(output_basepath, output_filename)).replace("\\", "/")
		print(f"{f'Rendering  {template_filename:<30}  ->  {output_filename}':<90} ...  ", end='')
		
		# template = self.jinja.get_template(os.path.join("templates", template_filename).replace("\\","/"))
		template = self.jinja.get_template(template_filename)
		rendered_output = template.render(data)
		
		if minify:
			rendered_output = htmlmin.minify(rendered_output, remove_empty_space=True)
		
		with open(output_filename, "w", encoding="utf8") as f:
			f.write(rendered_output)
			f.close()
		
		print("Done")
		
		self.rendered_pages.append(output_filename)
		return output_filename
