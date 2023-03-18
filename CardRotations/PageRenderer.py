import Config
from Common import Utility
from IdolDatabase import *

from . import CardValidity
from .CardUtility import CardUtility

import os
import sys
import math
import platform
import htmlmin
import base64
import copy
from datetime import datetime, timezone
from colorama import Fore, Style
from jinja2 import Environment, PackageLoader, FileSystemLoader, StrictUndefined
import jinja2.exceptions

class PageRenderException(Exception): pass

class PageRenderer():
	included_pages = set()
	tooltip_data = {} # Cards by ordinal
	
	def reset_included_pages(self):
		self.included_pages = set()
	
	def save_tooltip_data(self, output_filename):
		output_filepath = Utility.join_path(Config.OUTPUT_STAGE_DIRECTORY, output_filename)
		output_space = 145
		
		print()
		print(f"{f'{Fore.YELLOW}Saving     {Fore.WHITE}{Style.BRIGHT}tooltip data{Style.RESET_ALL}                    ->  {Fore.CYAN}{Style.BRIGHT}{output_filepath}':<{output_space}}{Style.RESET_ALL} ...  ", end='')
		
		with open(output_filepath, "w", encoding="utf-8") as output_file:
			output_file.write("const GLOBAL_TOOLTIP_DATA=")
			json.dump(self.tooltip_data, fp=output_file, separators=(',', ':'))
		
		print(f"{Fore.GREEN}{Style.BRIGHT}Done{Style.RESET_ALL}")
	
		# TEMPLATES_DIRECTORY
	
	def __init__(self, parent):
		self.parent = parent
		
		self.templates_directory_abspath = Utility.join_path(Config.ROOT_DIRECTORY, Config.TEMPLATES_DIRECTORY)
		
		self.jinja = Environment(
			loader    = FileSystemLoader(self.templates_directory_abspath, encoding='utf-8'),
			undefined = StrictUndefined,
			# loader=PackageLoader("CardRotations", encoding='utf-8')
		)
		
		def include(filename, static=False, minify_html=False, **kwargs):
			include_output = ""
			
			if static:
				root_directory = Utility.getter(kwargs, 'root_directory', Config.TEMPLATES_DIRECTORY)
				
				filename_path  = Utility.join_path(root_directory, filename)
				self.included_pages.add(filename_path)
				
				include_output = Utility.read_file(filename_path)
				if include_output == False:
					raise PageRenderException(f"Include failed (file read failure): {filename_path}")
				
			else: 
				try:
					template = self.jinja.get_template(filename)
				except jinja2.exceptions.TemplateNotFound:
					raise PageRenderException(f"Include failed (template not found): {filename}")
				
				template_filename_path = os.path.relpath(template.filename, start=Config.ROOT_DIRECTORY).replace('\\', '/')
				self.included_pages.add(template_filename_path)
				
				include_output = template.render({**kwargs})
			
			if minify_html:
				include_output = htmlmin.minify(include_output, remove_empty_space=True)
			
			return include_output
		
		def get_atlas_plane(ordinal):
			return parent.thumbnails.get_atlas_plane(ordinal)
			
		def embed_card_tooltip(card):
			if card.ordinal not in self.tooltip_data:
				self.tooltip_data[card.ordinal] = CardUtility.serialize_card(card)
			return card.ordinal
			
		def card_thumbnail_classes(card):
			return f"card-thumbnail group-{ card.group_id.value }-{ card.rarity.value }-{ get_atlas_plane(card.ordinal) } card-{ card.ordinal }"
		
		def cache_buster(filepath):
			busted_path = Utility.cache_buster(Config.OUTPUT_STAGE_DIRECTORY, filepath)
			return busted_path
		
		# ---------------------------------------------
		
		self.jinja.filters.update({
			'format_days'       : Utility.format_days,
			'format_years_days' : Utility.format_years_days,
			'format_delta_days' : Utility.format_delta_days,
			'pluralize'         : Utility.pluralize,
			'ordinalize'        : Utility.ordinalize,
			
			'conditional'       : Utility.conditional,
			'format_datestring' : Utility.format_datestring,
		})
		
		self.jinja.globals.update({
			# Python built in functions
			'len'                    : len,
			'int'                    : int,
			'range'                  : range,
			'reversed'               : reversed,
			
			'math'                   : math,
			
			# Application related variables
			'cmd_args'               : self.parent.args,
			
			# Application related global enums
			'Locale'                 : Locale,
			'Idols'                  : Idols,
			'Member'                 : Member,
			'Group'                  : Group,
			'Rarity'                 : Rarity,
			'Source'                 : Source,
			'Attribute'              : Attribute.get_valid(),
			'Type'                   : Type.get_valid(),
			
			'BannerType'             : BannerType.get_valid(),
			
			# Page specific functions
			'is_valid_card'          : CardValidity.is_valid_card,
			'is_missing_card'        : CardValidity.is_missing_card,
			'is_nonextant_card'      : CardValidity.is_nonextant_card,
			
			'include'                : include,
			
			'get_card_source_label'  : CardUtility.get_card_source_label,
			'card_to_base64'         : CardUtility.card_to_base64,
			'embed_card_tooltip'     : embed_card_tooltip,
			
			# Generic utility
			'concat'                 : Utility.concat,
			
			# Atlas
			'get_atlas_plane'        : get_atlas_plane,
			'card_thumbnail_classes' : card_thumbnail_classes,
			
			# Systems stuff
			'cache_buster'           : cache_buster,
		})
		
		self.rendered_pages = []
		
		self.reset_render_history()
		self.render_history_loaded = self.load_render_history()
		
	# -------------------------------------------------------------------------------------------
	
	def reset_render_history(self):
		self.render_history          = {}
		self.render_history_previous = {}
		self.render_history_loaded   = False
	
	def is_render_history_loaded(self):
		return self.render_history_loaded
		
	def load_render_history(self):
		try:
			with open(Config.RENDER_HISTORY_FILE, "r") as f:
				self.render_history = json.load(f)
			
			for template, data in self.render_history.items():
				data['last_used']    = datetime.fromisoformat(data['last_used'])
				data['output']       = set(data['output'])
				data['dependencies'] = set(data['dependencies'])
		except:
			self.render_history = {}
			return False
		
		self.render_history_previous = copy.deepcopy(self.render_history)
		return True
		
	def save_render_history(self):
		if not isinstance(self.render_history, dict):
			return False
			
		def json_serialize(obj):
		    if isinstance(obj, (datetime)):
		        return obj.isoformat()
		    if isinstance(obj, (set)):
		        return list(obj)
		        # return list([x.replace('\\', '/') for x in obj])
		    raise TypeError(f"Type {type(obj)} not serializable")
		
		with open(Config.RENDER_HISTORY_FILE, "w") as f:
			json.dump(self.render_history, f, default=json_serialize, indent=0 if not self.parent.args.dev else 4)
		
		return True
	
	def due_for_rendering(self, template_filename, print_log=True):
		template_filename_path = Utility.join_path(Config.TEMPLATES_DIRECTORY, template_filename)
		
		if self.has_template_changed(template_filename_path) or self.is_any_output_missing(template_filename_path):
			self.reset_output(template_filename_path)
			return True
			
		self.preserve_output(template_filename_path)
		if print_log:
			print(f"{Fore.BLACK}{Style.BRIGHT}Unchanged  {Fore.WHITE}{os.path.basename(template_filename):<30}{Style.RESET_ALL} ...  {Fore.GREEN}{Style.BRIGHT}OK{Style.RESET_ALL}")
		
		return False
	
	def has_template_changed(self, template_filename):
		if template_filename not in self.render_history_previous:
			return True
		if 'last_used' not in self.render_history_previous[template_filename]:
			return True
		
		file_modified_time = datetime.utcfromtimestamp(os.path.getmtime(template_filename)).replace(tzinfo=timezone.utc)
		
		if self.render_history_previous[template_filename]['last_used'] < file_modified_time:
			return True
			
		# Automatically check dependencies as well
		for depended_template in self.render_history_previous[template_filename]['dependencies']:
			if self.has_template_changed(depended_template):
				return True

		return False
		
	def is_any_output_missing(self, template_filename):
		if template_filename not in self.render_history_previous:
			return True
		if 'output' not in self.render_history_previous[template_filename]:
			return True
		# if len(self.render_history_previous[template_filename]['output']) == 0:
		# 	return True
			
		for output_filename in self.render_history_previous[template_filename]['output']:
			if not os.path.exists(output_filename):
				return True
				
		return False
	
	def reset_output(self, template_filename):
		if template_filename not in self.render_history:
			return False
		self.render_history[template_filename]['output'] = set()
	
	def preserve_output(self, template_filename):
		if template_filename not in self.render_history_previous:
			return False
		if 'output' not in self.render_history_previous[template_filename]:
			return False
			
		self.rendered_pages.extend(self.render_history_previous[template_filename]['output'])
	
	# -------------------------------------------------------------------------------------------
		
	def mark_rendered(self, template_filename, full_output_filepath, dependencies=[]):
		template_filename = Utility.join_path(template_filename)
		if template_filename not in self.render_history:
			self.render_history[template_filename] = {
				'last_used'    : None,
				'output'       : set(),
				'dependencies' : set(),
			}
			
		self.render_history[template_filename]['last_used'] = datetime.now(timezone.utc)
		self.render_history[template_filename]['output'].add(full_output_filepath)
		
		dependencies = [dependency.replace('\\', '/') for dependency in dependencies]
		self.render_history[template_filename]['dependencies'].update(set(dependencies))
		
	
	def make_output_filepath(self, output_filename, output_basepath=None):
		if output_basepath == None:
			output_basepath = Config.OUTPUT_STAGE_DIRECTORY
		return Utility.join_path(output_basepath, output_filename, normalize=True)
	
	@staticmethod
	def can_minify_as_html(filename):
		minifiable_extensions = ['.html', '.php']
		for extension in minifiable_extensions:
			if filename.endswith(extension):
				return True
		return False
	
	def render_and_save(self, template_filename, output_filename, data, minify_html=True, output_basepath=None, generated_note=False, dependencies=[]):
		try:
			template = self.jinja.get_template(template_filename)
		except jinja2.exceptions.TemplateNotFound:
			print(f"{Fore.RED}{Style.BRIGHT}Template not found:   {Fore.WHITE}{template_filename:<40}  {Fore.YELLOW}(Directory: {self.templates_directory_abspath}){Style.RESET_ALL}")
			return False
		
		template_filename_path = os.path.relpath(template.filename, start=Config.ROOT_DIRECTORY)
		
		full_output_filepath = self.make_output_filepath(
			output_filename = output_filename,
			output_basepath = output_basepath)
		
		output_space = 145
		
		output_filename_full = output_filename
		if output_basepath != None:
			output_filename_full = Utility.join_path(output_basepath, output_filename)
		print(f"{f'{Fore.YELLOW}Rendering  {Fore.WHITE}{Style.BRIGHT}{template_filename:<30}{Style.RESET_ALL}  ->  {Fore.CYAN}{Style.BRIGHT}{output_filename_full}':<{output_space}}{Style.RESET_ALL} ...  ", end='')
		
		self.reset_included_pages()
		rendered_output = template.render(data)
		
		dependencies = self.included_pages.union(dependencies)
		self.mark_rendered(template_filename_path, full_output_filepath, dependencies)
		
		for filename in dependencies:
			self.mark_rendered(Utility.join_path(filename), full_output_filepath)
		
		if minify_html and self.can_minify_as_html(template_filename):
			rendered_output = htmlmin.minify(rendered_output, remove_empty_space=True)
		
		with open(full_output_filepath, "w", encoding="utf8") as f:
			if generated_note:
				try:
					comment_prefix = {
						'js'        : '//',
						'htaccess'  : '#',
						'py'        : '#',
						
					}[output_filename.rsplit('.', 2)[1]]
				except KeyError:
					comment_prefix = '#'
					
				f.write(f"{comment_prefix} ------------------------------------------------------------\n")
				f.write(f"{comment_prefix} DO NOT MODIFY THIS FILE DIRECTLY\n")
				f.write(f"{comment_prefix} This file was auto generated from {template_filename}\n")
				f.write(f"{comment_prefix} ------------------------------------------------------------\n")
			f.write(rendered_output)
			f.close()
		
		print(f"{Fore.GREEN}{Style.BRIGHT}Done{Style.RESET_ALL}")
		
		self.rendered_pages.append(full_output_filepath)
		return full_output_filepath
