import os
import re
import time
import glob
import csscompressor
from colorama import Fore, Style

import warnings
with warnings.catch_warnings():
	# stfu about stuff I didn't write
	warnings.simplefilter(action='ignore', category=FutureWarning)
	from scss import Compiler
	import scss.errors

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ResourceProcessor():
	def __init__(self, parent):
		self.parent = parent
	
	def _fix_scss_bullshit(self, code):
		def repl(m):
			divide = lambda s, d: list(map(''.join, zip(*[iter(s)]*d)))
			c = [int(x * (3 - len(x)), 16) for x in divide(m.group(1), len(m.group(1)) // 3)]
			if len(c) == 4:
				return f"rgba({c[0]}, {c[1]}, {c[2]}, {(c[3] / 255):0.3f})"
			else:
				return "#" + m.group(1)
		
		pattern = re.compile(r'(?<=[^0-9a-f])#([0-9a-f]{3,8})(?=[^0-9a-f])', re.MULTILINE | re.IGNORECASE)
		return pattern.sub(repl, code)
	
	def compile_css(self, input_files, output_file, minify=True):
		scss_compiler = Compiler()

		compiled_code = []
		unminified_size = 0
		minified_size = 0
		
		print(f"\n{Fore.GREEN}{Style.BRIGHT}Starting CSS compilation...{Style.RESET_ALL}")
		
		for filepath in input_files:
			print(f"  {Fore.WHITE}{Style.BRIGHT}{filepath:<37}{Style.RESET_ALL}  ", end='')
			
			try:
				css_code = open(filepath, "r", encoding="utf8").read()
			except:
				print(f"  {Fore.RED}Failed to open file...{Style.RESET_ALL}")
				continue
				
			if '.scss' in filepath:
				print(f"  {Fore.MAGENTA}{Style.BRIGHT}Compiling SCSS...{Style.RESET_ALL}", end='')
				try:
					css_code = self._fix_scss_bullshit(css_code)
					css_code = scss_compiler.compile_string(css_code)
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
				unminified_size += len(css_code)
				css_code = csscompressor.compress(css_code, max_linelen=20480)
				minified_size += len(css_code)
			
			print(f"  {Fore.GREEN}{Style.BRIGHT}Done!{Style.RESET_ALL}")
			compiled_code.append((filepath, css_code))
		
		if minify:
			print(f"  {Fore.YELLOW}CSS Minify reduced size from {unminified_size / 1024:.2f} KB to {minified_size / 1024:.2f} KB. Yay!{Style.RESET_ALL}")
		
		with open(output_file, "w", encoding="utf8") as f:
			for source_path, minified in compiled_code:
				f.write(f"/* {os.path.basename(source_path)} */\n")
				f.write(minified)
				f.write("\n")
		
		print(f"  {Fore.GREEN}{Style.BRIGHT}Compile done! Output written to file:    {Fore.BLUE}{output_file}{Style.RESET_ALL}")
		print()
	
	# ---------------------------------------------------------------
	
	class EventHandler(FileSystemEventHandler):
		is_dirty = False
		
		def __init__(self, parent, watched_files, input_files, output_file):
			super().__init__()
			
			self.parent = parent
			
			self.watched_files = []
			for input_file in watched_files:
				self.watched_files.extend([x.replace('\\', '/') for x in glob.glob(input_file)])
			
			self.input_files = input_files
			self.output_file = output_file
		
		def on_modified(self, event):
			if self.is_dirty: return
			if event.is_directory: return
			
			file_path = event.src_path.replace('\\', '/')
			if file_path not in self.watched_files: return
				
			print(f"{Fore.YELLOW}{Style.BRIGHT}File changed:   {Fore.BLUE}{file_path}{Style.RESET_ALL}")
			self.is_dirty = True
		
		def compile(self):
			if not self.is_dirty: return
			
			self.parent.compile_css(
				input_files = self.input_files,
				output_file = self.output_file,
				minify=False,
			)
			self.is_dirty = False
	
	def watch_changes(self):
		event_handler = self.EventHandler(self,
			watched_files = self.parent.css_settings.watched_files,
			input_files   = self.parent.css_settings.input_files,
			output_file   = self.parent.css_settings.output_file,
		)
		
		observer = Observer()
		observer.schedule(event_handler, self.parent.css_settings.watch_directory, recursive=True)
		observer.start()
		
		print()
		print( "------------------------------------------------------")
		print(f"  {Fore.MAGENTA}{Style.BRIGHT}Watching for file changes!{Style.RESET_ALL}")
		print(f"  {Fore.GREEN}{Style.BRIGHT}Directory        : {Fore.BLUE}{self.parent.css_settings.watch_directory}{Style.RESET_ALL}")
		print(f"  {Fore.GREEN}{Style.BRIGHT}Watched files    : {Fore.BLUE}{', '.join(self.parent.css_settings.watched_files)}{Style.RESET_ALL}")
		print()
		
		try:
			while True:
				event_handler.compile()
				time.sleep(0.5)
		except KeyboardInterrupt:
			observer.stop()
		
		print(f"{Fore.BLUE}It is time to go to sleep! Good night...{Style.RESET_ALL}")
		observer.join()
