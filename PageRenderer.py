import os
import math
import platform
import htmlmin
import base64
import copy
from datetime import datetime, timezone
from colorama import Fore, Style
from jinja2 import Environment, PackageLoader, FileSystemLoader, select_autoescape

from IdolDatabase import *
from Utility import *
import CardValidity

class PageRenderer():
	RENDER_HISTORY_FILE = "render_history.json"
	
	included_pages = set()
	tooltip_data = {
		'cards'   : {},
		'members' : {},
	}
	
	def reset_included_pages(self):
		self.included_pages = set()
	
	def save_tooltip_data(self, output_filename):
		output_filepath = os.path.join(self.parent.OutputDirectory, output_filename).replace("\\", "/")
		
		print()
		print(f"{Fore.YELLOW}Saving tooltip data                        ->  {Fore.CYAN}{Style.BRIGHT}{output_filepath}{Style.RESET_ALL}                 ...  ", end='')
		
		with open(output_filepath, "w", encoding="utf-8") as output_file:
			output_file.write("GLOBAL_TOOLTIP_DATA=")
			json.dump(self.tooltip_data, fp=output_file, separators=(',', ':'))
		
		print(f"{Fore.GREEN}{Style.BRIGHT}Done{Style.RESET_ALL}")
	
	
	def __init__(self, parent):
		self.parent = parent
		
		self.jinja = Environment(
			# loader=FileSystemLoader(os.path.dirname(os.path.abspath(__file__)), encoding='utf-8'),
			loader=PackageLoader("CardRotations", encoding='utf-8'),
			# autoescape=select_autoescape()
		)
		
		def include_static(filename, minify=False, root_directory="templates"):
			self.included_pages.add(filename)
			return Utility.include_static(filename, minify=minify, root_directory=root_directory)
			
		def render_included(template_filename, data = {}, **kwargs):
			self.included_pages.add(template_filename)
			for k, v in kwargs.items(): data[k] = v
			template = self.jinja.get_template(template_filename)
			return template.render(data)
		
		def get_atlas_plane(ordinal):
			return parent.thumbnails.get_atlas_plane(ordinal)
			
		def embed_card_tooltip(card):
			if card.ordinal not in self.tooltip_data['cards']:
				self.tooltip_data['cards'][card.ordinal] = Utility.serialize_card(card)
			return card.ordinal
		
		def embed_member_tooltip(member):
			if member.value not in self.tooltip_data['members']:
				self.tooltip_data['members'][member.value] = Utility.serialize_member(member)
			return member.value
			
		# ---------------------------------------------
		
		self.jinja.filters.update({
			'format_days'       : Utility.format_days,
			'format_years_days' : Utility.format_years_days,
			'format_delta_days' : Utility.format_delta_days,
			'pluralize'         : Utility.pluralize,
			'ordinalize'        : Utility.ordinalize,
			
			'conditional_css'   : Utility.conditional_css,
			'format_datestring' : Utility.format_datestring,
		})
		
		self.jinja.globals.update({
			# Python built in functions
			'len'                   : len,
			'range'                 : range,
			'reversed'              : reversed,
			
			# Application related variables
			'cmd_args'              : self.parent.args,
			
			# Application related global enums
			'Locale'                : Locale,
			'Idols'                 : Idols,
			'Member'                : Member,
			'Group'                 : Group,
			'Rarity'                : Rarity,
			'Source'                : Source,
			'Attribute'             : Attribute.get_valid(),
			'Type'                  : Type.get_valid(),
			
			'BannerType'            : BannerType.get_valid(),
			
			# Page specific functions
			'is_valid_card'         : CardValidity.is_valid_card,
			'is_missing_card'       : CardValidity.is_missing_card,
			'is_nonextant_card'     : CardValidity.is_nonextant_card,
			'get_card_source_label' : Utility.get_card_source_label,
			
			'include_static'        : include_static,
			'render_included'       : render_included,
			
			'embed_card_tooltip'    : embed_card_tooltip,
			'embed_member_tooltip'  : embed_member_tooltip,
			
			'card_to_base64'        : Utility.card_to_base64,
			'member_to_base64'      : Utility.member_to_base64,
			
			# Atlas
			'get_atlas_plane'       : get_atlas_plane,
			
			# Systems stuff
			'cache_buster'          : lambda filepath: Utility.cache_buster(self.parent.OutputDirectory, filepath),
		})
		
		self.rendered_pages = []
		self.load_render_history()
		
	# -------------------------------------------------------------------------------------------
	
	def reset_render_history(self):
		self.render_history = {}
		
	def load_render_history(self):
		self.render_history = {}
		if os.path.exists(self.RENDER_HISTORY_FILE):
			try:
				with open(self.RENDER_HISTORY_FILE, "r") as f:
					self.render_history = json.load(f)
				
				for template, data in self.render_history.items():
					data['last_used'] = datetime.fromisoformat(data['last_used'])
					data['output']    = set(data['output'])
					data['embedded']  = set(data['embedded'])
			except:
				self.render_history = {}
		
		self.render_history_previous = copy.deepcopy(self.render_history)
		
	def save_render_history(self):
		if not isinstance(self.render_history, dict):
			return False
			
		def json_serialize(obj):
		    if isinstance(obj, (datetime)):
		        return obj.isoformat()
		    if isinstance(obj, (set)):
		        return list(obj)
		    raise TypeError(f"Type {type(obj)} not serializable")
		
		with open(self.RENDER_HISTORY_FILE, "w") as f:
			json.dump(self.render_history, f, default=json_serialize)
		
		return True
	
	def has_template_changed(self, template_filename):
		if template_filename not in self.render_history_previous:
			return True
		if 'last_used' not in self.render_history_previous[template_filename]:
			return True
		
		template_filename_path = os.path.join("templates", template_filename)
		file_modified_time = datetime.utcfromtimestamp(os.path.getmtime(template_filename_path)).replace(tzinfo=timezone.utc)
		
		if self.render_history_previous[template_filename]['last_used'] < file_modified_time:
			return True
			
		# Automatically check embedded templates as well
		for embedded_template in self.render_history_previous[template_filename]['embedded']:
			if self.has_template_changed(embedded_template): return True
		
		return False
		
	def is_any_output_missing(self, template_filename):
		if template_filename not in self.render_history_previous:
			return True
		if 'output' not in self.render_history_previous[template_filename]:
			return True
		if len(self.render_history_previous[template_filename]['output']) == 0:
			return True
			
		for output_filename in self.render_history_previous[template_filename]['output']:
			if not os.path.exists(output_filename):
				return True
				
		return False
	
	def reset_output(self, template_filename):
		if template_filename not in self.render_history:
			return False
		self.render_history[template_filename]['output'] = set()
	
	def preserve_output(self, template_filename):
		print(f"{Fore.BLACK}{Style.BRIGHT}Unchanged  {Fore.WHITE}{template_filename:<30}{Style.RESET_ALL} ...  {Fore.GREEN}{Style.BRIGHT}OK{Style.RESET_ALL}")
		
		if template_filename not in self.render_history_previous:
			return False
		if 'output' not in self.render_history_previous[template_filename]:
			return False
			
		self.rendered_pages.extend(self.render_history_previous[template_filename]['output'])
	
	# -------------------------------------------------------------------------------------------
		
	def mark_rendered(self, template_filename, full_output_filepath, embedded_templates=[]):
		if template_filename not in self.render_history:
			self.render_history[template_filename] = {
				'last_used' : None,
				'output'    : set(),
				'embedded'  : set(),
			}
		self.render_history[template_filename]['last_used'] = datetime.now(timezone.utc)
		self.render_history[template_filename]['output'].add(full_output_filepath)
		self.render_history[template_filename]['embedded'].update(set(embedded_templates))
		
	
	def make_output_filepath(self, output_filename, output_basepath=None):
		if output_basepath == None:
			output_basepath = self.parent.OutputDirectory
		return os.path.normpath(os.path.join(output_basepath, output_filename)).replace("\\", "/")
		
		
	def render_and_save(self, template_filename, output_filename, data, minify=True, output_basepath=None, generated_note=False, auxiliary_templates=[]):
		template = self.jinja.get_template(template_filename)
		
		full_output_filepath = self.make_output_filepath(
			output_filename = output_filename,
			output_basepath = output_basepath)
		
		num_slashes = output_filename.count('/')
		output_space = 115 + max(0, num_slashes - 1) * 10
		
		print(f"{f'{Fore.YELLOW}Rendering  {Fore.WHITE}{Style.BRIGHT}{template_filename:<30}{Style.RESET_ALL}  ->  {Fore.CYAN}{Style.BRIGHT}{output_filename}':<{output_space}}{Style.RESET_ALL} ...  ", end='')
		
		self.reset_included_pages()
		rendered_output = template.render(data)
		
		embedded_templates = self.included_pages.union(auxiliary_templates)
		self.mark_rendered(template_filename, full_output_filepath, embedded_templates)
		
		for filename in embedded_templates:
			self.mark_rendered(filename, full_output_filepath)
		
		if minify:
			rendered_output = htmlmin.minify(rendered_output, remove_empty_space=True)
		
		with open(full_output_filepath, "w", encoding="utf8") as f:
			if generated_note:
				f.write(f"# ------------------------------------------------------------\n")
				f.write(f"# DO NOT MODIFY THIS FILE DIRECTLY\n")
				f.write(f"# This file was auto generated from {template_filename}\n")
				f.write(f"# ------------------------------------------------------------\n")
			f.write(rendered_output)
			f.close()
		
		print(f"{Fore.GREEN}{Style.BRIGHT}Done{Style.RESET_ALL}")
		
		self.rendered_pages.append(full_output_filepath)
		return full_output_filepath
