import Config
from Common import Utility

import os
import sys
import re
import time
import glob
import json
import signal
import psutil

from colorama import Fore, Style
from datetime import datetime
from watchdog.events import FileSystemEventHandler

from .ResourceProcessor import ProcessorResult

class _WatchEventHandler(FileSystemEventHandler):
	is_dirty = True
	
	def __init__(self, parent, task_name, task_config):
		super().__init__()
		
		self.parent        = parent
		self.task_name     = task_name
		self.task_config   = task_config
		self.files_changed = set()
	
	
	def on_modified(self, event):
		if self.is_dirty: return
		if event.is_directory: return
		
		watched_files_globbed = Utility.glob(self.task_config.watched_files)
		
		file_path = event.src_path.replace('\\', '/')
		if file_path not in watched_files_globbed: return
		
		self.is_dirty = True
		self.files_changed.add(file_path)
		
	
	def run_task(self):
		if not self.is_dirty: return
		if self.parent.processing:
			return
		
		for file_path in self.files_changed:
			print(f"{Fore.YELLOW}{Style.BRIGHT}File changed:   {Fore.BLUE}{file_path}{Style.RESET_ALL}\n")
		
		self.parent.processing = True
		
		self.parent.process_task(self.task_name)
		
		self.parent.processing = False
		self.clean()
	
	def clean(self):
		self.is_dirty = False
		self.files_changed.clear()



class FileProcessorWatcher():
	def __init__(self, processor, kill_duplicates):
		self.processor = processor
		
		if kill_duplicates:
			self.kill_duplicate_processes()
		
		
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
				if 'python' not in p.name().lower():
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
			print()
			
		
	def clear_queue(self):
		for event_handler in self.event_handlers.values():
			event_handler.clean()
	
	
	def process_task(self, task_name):
		self.processor.history.load()
		processor_result = self.processor.run_processor(task_name, minify=False)
		self.processor.history.save()
		
		if processor_result == ProcessorResult.Success:
			now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			print(f"    {Fore.YELLOW}{Style.BRIGHT}{Fore.YELLOW}Completed on {Fore.WHITE}{now}{Style.RESET_ALL}")
		
		elif processor_result == ProcessorResult.Failure:
			self.clear_queue()
			now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
			print(f"    {Fore.RED}{Style.BRIGHT}{Fore.YELLOW}Aborted on {Fore.WHITE}{now}{Style.RESET_ALL}")
			
		print()
		
	
	def start_watching(self, polling = False):
		print( "---------------------------------------------------------------")
		print(f"  {Fore.MAGENTA}{Style.BRIGHT}Watching for file changes!{Style.RESET_ALL}")
		
		if polling:
			from watchdog.observers.polling import PollingObserver as Observer
		else:
			from watchdog.observers import Observer
		
		observer = Observer()
		
		self.event_handlers = {}
		for task_name, task_config in self.processor.tasks.items():
			self.event_handlers[task_name] = _WatchEventHandler(self, task_name, task_config)
			observer.schedule(self.event_handlers[task_name], task_config.watch_directory, recursive=True)
			
			print()
			print(f"  {Fore.WHITE}{Style.BRIGHT}Processor        {Fore.WHITE}: {Fore.BLUE}{task_name.upper()}{Style.RESET_ALL}")
			print(f"  {Fore.GREEN}{Style.BRIGHT}Directory        {Fore.WHITE}: {Fore.BLUE}{task_config.watch_directory}{Style.RESET_ALL}")
			print(f"  {Fore.GREEN}{Style.BRIGHT}Watched files    {Fore.WHITE}: {Fore.BLUE}{', '.join(task_config.watched_files)}{Style.RESET_ALL}")
		
		print()
		print(f"  {Fore.YELLOW}{Style.BRIGHT}Polling Observer {Fore.WHITE}: {'yes' if polling else 'no'}{Style.RESET_ALL}")
		print()
		
		observer.start()
		
		self.running = True
		
		def signal_handler(signum, frame):
			self.running = False
		
		signal.signal(signal.SIGINT, signal_handler)
		signal.signal(signal.SIGTERM, signal_handler)
		
		self.processing = False;
		
		while self.running:
			for event_handler in self.event_handlers.values():
				event_handler.run_task()
			time.sleep(0.1)
			
		print(f"{Fore.BLUE}It is time to go to sleep! Good night...{Style.RESET_ALL}\n")
		
		observer.unschedule_all()
		observer.stop()
		observer.join()
