import Config
from .Utility import Utility

import os
import sys
import re
import time
import glob
import json
from datetime import datetime, timezone
from colorama import Fore, Style
import signal

import sass
import csscompressor
from rjsmin import jsmin
import htmlmin

from threading import Lock
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import psutil

# ------------------------------------------------

class ResourceProcessorImplementation():
	comment_format       = "/* {} */"
	file_prologue        = ""
	file_epilogue        = ""
	before_concatenation = ""
	after_concatenation  = ""
	indentation          = 0
	
	def needs_compilation(self, filepath):
		raise NotImplementedError()
	
	def compile(self, source_code, filepath):
		raise NotImplementedError()
		
	def minify(self, source_code, filepath):
		raise NotImplementedError()
	
	def process(self, input_files, output_file, minify=True):
		compiled_code   = []
		unminified_size = 0
		minified_size   = 0
		
		for input_filepath in input_files:
			print(f"    {Fore.WHITE}{Style.BRIGHT}{input_filepath:<47}{Style.RESET_ALL}  ", end='')
			
			try:
				source_code = open(input_filepath, "r", encoding="utf-8").read()
			except:
				print(f"  {Fore.RED}Failed to open file...{Style.RESET_ALL}")
				continue
				
			if self.needs_compilation(input_filepath):
				print(f"  {Fore.MAGENTA}{Style.BRIGHT}Compiling...{Style.RESET_ALL}", end='')
				try:
					source_code = self.compile(source_code, input_filepath)
				except Exception as e:
					print(f"  {Fore.RED}Failed! ({type(e).__name__})")
					print()
					print("----------------------------------------------------------------------------------------------")
					print(str(e))
					print("----------------------------------------------------------------------------------------------")
					print(f"{Style.RESET_ALL}")
					return False
			
			if minify:
				print(f"  {Fore.BLUE}{Style.BRIGHT}Minifying...{Style.RESET_ALL}", end='')
				unminified_size += len(source_code)
				source_code = self.minify(source_code, input_filepath)
				minified_size += len(source_code)
			
			print(f"  {Fore.GREEN}{Style.BRIGHT}Done!{Style.RESET_ALL}")
			compiled_code.append((input_filepath, source_code))
		
		if minify:
			print(f"    {Fore.YELLOW}Minify reduced file size from {unminified_size / 1024:.2f} KB to {minified_size / 1024:.2f} KB. Yay!{Style.RESET_ALL}")
		
		indentation = ''
		if isinstance(self.indentation, int) and self.indentation > 0:
			indentation = '\t' * self.indentation
		elif isinstance(self.indentation, str):
			indentation = self.indentation
		
		with open(output_file, "w", encoding="utf-8") as file:	
			if self.file_prologue:
				file.write(self.file_prologue + "\n")
				
			for source_path, source_code in compiled_code:
				file.write(indentation)
				file.write(self.comment_format.format(source_path))
				file.write("\n")
				
				if self.before_concatenation:
					file.write(indentation)
					file.write(self.before_concatenation)
					file.write("\n")
					
				file.write(indentation)
				file.write(source_code)
				file.write("\n")
				
				file.write(self.after_concatenation)
				file.write("\n")
				
				file.flush()
				
			if self.file_epilogue:
				file.write(self.file_epilogue + "\n")
		
# ---------------------------------------------------

class CSSResourceProcessor(ResourceProcessorImplementation):
	comment_format      = "/* {} */"
	after_concatenation = ""
	
	def needs_compilation(self, filepath):
		return '.scss' in filepath
	
	def compile(self, source_code, filepath):
		if not source_code:
			return ''
		
		try:
			return sass.compile(string=source_code)
		except sass.CompileError as e:
			raise e
			
		return ''
	
	def minify(self, source_code, filepath):
		return csscompressor.compress(source_code, max_linelen=20480)
	
	# def fix_scss_bullshit(self, code):
	# 	def repl(m):
	# 		divide = lambda s, d: list(map(''.join, zip(*[iter(s)]*d)))
	# 		c = [int(x * (3 - len(x)), 16) for x in divide(m.group(1), len(m.group(1)) // 3)]
	# 		if len(c) == 4:
	# 			return f"rgba({c[0]}, {c[1]}, {c[2]}, {(c[3] / 255):0.3f})"
	# 		else:
	# 			return "#" + m.group(1)
		
	# 	pattern = re.compile(r'(?<=[^0-9a-f])#([0-9a-f]{3,8})(?=[^0-9a-f])', re.MULTILINE | re.IGNORECASE)
	# 	return pattern.sub(repl, code)
	
# ---------------------------------------------------

class JavascriptResourceProcessor(ResourceProcessorImplementation):
	file_prologue       = "'use strict';\n"
	comment_format      = "/***********************************************\n *  {}\n */"
	after_concatenation = ";"
	
	def needs_compilation(self, filepath):
		return False
	
	def compile(self, source_code, filepath):
		return source_code
		
	def minify(self, source_code, filepath):
		return jsmin(source_code)
	
# ---------------------------------------------------

class TooltipsResourceProcessor(ResourceProcessorImplementation):
	comment_format    = "/* {} */"
	file_prologue     = "app.run(($templateCache) =>\n{"
	file_epilogue     = "});"
	indentation       = 1
	
	def needs_compilation(self, filepath):
		return True
	
	def compile(self, source_code, filepath):
		source_code = ''.join([x.strip() for x in source_code.split('\n')])
		source_code = htmlmin.minify(source_code)
		source_code = source_code.replace("'", "\\'")
		return f"$templateCache.put('tooltips/{os.path.basename(filepath)}', '{source_code}');"
		
	def minify(self, source_code, filepath):
		return source_code
	
# ---------------------------------------------------

class ResourceProcessorException(Exception): pass
class ResourceProcessor():
	def __init__(self, parent, settings):
		self.parent   = parent
		self.settings = settings
		self.processors_ran = set()
		
		for processor_name, processor_settings in self.settings.items():
			processor_settings.processor_instance = processor_settings.processor()
		
		self.mutex = Lock()
		
		self.load_processor_history()
	
	# -------------------------------------------------------------
	
	def processor_history_loaded_successfully(self):
		return self.processor_history_loaded
		
	def load_processor_history(self):
		self.processor_history = {}
		self.processor_history_loaded = False
		
		if os.path.exists(Config.PROCESSOR_HISTORY_FILE):
			try:
				with open(Config.PROCESSOR_HISTORY_FILE, "r") as f:
					self.processor_history = json.load(f)
				
				for processor_name, data in self.processor_history.items():
					data['last_processed'] = datetime.fromisoformat(data['last_processed'])
					data['input_files']    = set(data['input_files'])
				
				self.processor_history_loaded = True
			except Exception as e:
				self.processor_history = {}
		
	def save_processor_history(self):
		if not isinstance(self.processor_history, dict):
			return False
			
		def json_serialize(obj):
		    if isinstance(obj, (datetime)):
		        return obj.isoformat()
		    if isinstance(obj, (set)):
		        return list(obj)
		    raise TypeError(f"Type {type(obj)} not serializable")
		
		with open(Config.PROCESSOR_HISTORY_FILE, "w") as f:
			json.dump(self.processor_history, f, default=json_serialize)
		
		return True
	
	
	def should_run_processor(self, processor_name):
		if processor_name not in self.processor_history:
			return True
		if 'last_processed' not in self.processor_history[processor_name]:
			return True
		
		if not os.path.exists(self.settings[processor_name].output_file):
			return True
		
		if self.settings[processor_name].output_file != self.processor_history[processor_name]['output_file']:
			return True
		
		input_files_globbed = Utility.glob(self.settings[processor_name].input_files)
		
		for input_file in input_files_globbed:
			if input_file not in self.processor_history[processor_name]['input_files']:
				return True
		
			file_modified_time = datetime.utcfromtimestamp(os.path.getmtime(input_file)).replace(tzinfo=timezone.utc)
			if self.processor_history[processor_name]['last_processed'] < file_modified_time:
				return True
		
		for input_file in self.processor_history[processor_name]['input_files']:
			if input_file not in input_files_globbed:
				return True
		
		return False
		
	
	def mark_processed(self, processor_name, input_files, output_file):
		self.processor_history[processor_name] = {
			'last_processed' : datetime.now(timezone.utc),
			'input_files'    : set(input_files),
			'output_file'    : output_file,
		}
	
	
	def process_all_resources(self, force=False, minify=True):
		self.processors_ran = set()
		
		print()
		for processor_name, processor_settings in self.settings.items():
			if processor_name not in self.processors_ran:
				self.run_processor(processor_name, force=force, minify=minify)
				print()
		
		self.save_processor_history()
	
	# -------------------------------------------------------------------------
	
	def run_processor(self, processor_name, force=False, minify=True):
		if processor_name not in self.settings:
			raise ResourceProcessorException("Processor name not configured: " + processor_name)
		
		self.processors_ran.add(processor_name)
		
		settings = self.settings[processor_name]
		
		if 'depends' in settings:
			for dependent_processor_name in settings.depends:
				if force or self.should_run_processor(dependent_processor_name):
					print(f"{Fore.YELLOW}{Style.BRIGHT}{processor_name.upper()} resource processor depends on {dependent_processor_name.upper()}  ...  {Style.RESET_ALL}", end='')
					self.run_processor(dependent_processor_name, minify=minify)
					print()
					force = True
		
		print(f"{Fore.GREEN}{Style.BRIGHT}Processing {processor_name.upper()}...{Style.RESET_ALL}")
		
		if not force and not self.should_run_processor(processor_name):
			print(f"    {Fore.BLACK}{Style.BRIGHT}Source files unchanged                ...  OK{Style.RESET_ALL}")
			return False
		
		input_files_globbed = Utility.glob(settings.input_files)
		
		settings.processor_instance.process(
			input_files  = input_files_globbed,
			output_file  = settings.output_file,
			minify       = minify
		)
		
		self.mark_processed(processor_name, input_files_globbed, settings.output_file)
		
		print(f"    {Fore.GREEN}{Style.BRIGHT}Processing complete!    {Fore.YELLOW}Output written to file:    {Fore.BLUE}{settings.output_file}{Style.RESET_ALL}")
		return True
	
	# -------------------------------------------------------------------------
	
	class EventHandler(FileSystemEventHandler):
		is_dirty = True
		
		def __init__(self, parent, processor_name, processor_settings):
			super().__init__()
			
			self.parent             = parent
			self.processor_name     = processor_name
			self.processor_settings = processor_settings
			self.files_changed      = set()
		
		
		def on_modified(self, event):
			if self.is_dirty: return
			if event.is_directory: return
			
			watched_files_globbed = Utility.glob(self.processor_settings.watched_files)
			
			file_path = event.src_path.replace('\\', '/')
			if file_path not in watched_files_globbed: return
			
			self.is_dirty = True
			self.files_changed.add(file_path)
		
		
		def compile(self):
			if not self.is_dirty: return
			if self.parent.processing:
				print(f"{Fore.RED}ALREADY PROCESSING SNOOZE")
				return
			
			for file_path in self.files_changed:
				print(f"{Fore.YELLOW}{Style.BRIGHT}File changed:   {Fore.BLUE}{file_path}{Style.RESET_ALL}\n")
			
			self.parent.processing = True
			
			self.parent.load_processor_history()
			processor_ran = self.parent.run_processor(self.processor_name, minify=False)
			self.parent.save_processor_history()
			
			if processor_ran:
				now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
				print(f"    {Fore.YELLOW}{Style.BRIGHT}{Fore.YELLOW}Completed on {Fore.WHITE}{now}{Style.RESET_ALL}")
			print()
			
			self.parent.processing = False
			
			self.is_dirty = False
			self.files_changed.clear()
	
	
	def kill_duplicate_processes(self):
		main_file = os.path.basename(sys.modules['__main__'].__file__)
		
		myself = psutil.Process(os.getpid())
		ignored_processes = [myself] + [p for p in myself.parents()] + [p for p in myself.children(True)]
		ignored_pids = set([p.pid for p in ignored_processes])
		
		duplicate_processes = []
		for p in psutil.process_iter():
			with p.oneshot():
				if p.pid in ignored_pids:
					continue
				if 'python' not in p.name():
					continue
				if p.cwd() != os.getcwd():
					continue
				
				cmdline = ' '.join(p.cmdline())
				if main_file + ' --watch' not in cmdline:
					continue
			
				duplicate_processes.append(p)
		
		if duplicate_processes:
			for p in duplicate_processes:
				p.kill()
			print(f"  {Fore.RED}{Style.BRIGHT}Watcher was already running. {Fore.YELLOW}Killed {len(duplicate_processes)} duplicate processes.{Style.RESET_ALL}")
		
		
	def watch_changes(self):
		self.kill_duplicate_processes()
		
		print()
		print( "---------------------------------------------------------------")
		print(f"  {Fore.MAGENTA}{Style.BRIGHT}Watching for file changes!{Style.RESET_ALL}")
		
		observer = Observer()
		
		event_handlers = {}
		for processor_name, processor_settings in self.settings.items():
			event_handlers[processor_name] = self.EventHandler(self, processor_name, processor_settings)
			observer.schedule(event_handlers[processor_name], processor_settings.watch_directory, recursive=True)
			
			print()
			print(f"  {Fore.WHITE}{Style.BRIGHT}Processor        : {Fore.BLUE}{processor_name.upper()}{Style.RESET_ALL}")
			print(f"  {Fore.GREEN}{Style.BRIGHT}Directory        : {Fore.BLUE}{processor_settings.watch_directory}{Style.RESET_ALL}")
			print(f"  {Fore.GREEN}{Style.BRIGHT}Watched files    : {Fore.BLUE}{', '.join(processor_settings.watched_files)}{Style.RESET_ALL}")
		
		print()
		
		observer.start()
		
		self.running = True
		
		def signal_handler(signum, frame):
			self.running = False
		
		signal.signal(signal.SIGINT, signal_handler)
		signal.signal(signal.SIGTERM, signal_handler)
		
		self.processing = False;
		
		while self.running:
			for event_handler in event_handlers.values():
				event_handler.compile()
			time.sleep(0.1)
			
		print(f"{Fore.BLUE}It is time to go to sleep! Good night...{Style.RESET_ALL}\n")
		
		observer.unschedule_all()
		observer.stop()
		observer.join()
