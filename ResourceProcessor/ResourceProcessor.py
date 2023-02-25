import Config
from Common import Utility

import os
import sys
import re
import time
import glob
import json
from datetime import datetime, timezone
from colorama import Fore, Style

from typing import List, Optional, Tuple, Dict, Type, Any

from enum import Enum

import htmlmin
import subprocess

from .FileProcessorBase import FileProcessorBase
from .ProcessorHistory import ProcessorHistory
from .ProcessorTask import ProcessorTask

# ---------------------------------------------------

class ProcessorResult(Enum):
	NotProcessed = 0
	Success      = 1
	Failure      = 2

class ResourceProcessorException(Exception): pass
class ResourceProcessor():
	
	tasks: Dict[str, ProcessorTask] = {}
	
	def __init__(self, parent, tasks: List[ProcessorTask]):
		self.parent = parent
		self.history = ProcessorHistory(Config.PROCESSOR_HISTORY_FILE)
		
		for task_config in tasks:
			# task_config.parent = self
			self.tasks[task_config.name] = task_config
			
			if task_config.file_processor:
				task_config.processor_instance = task_config.file_processor()
		
		self.tasks_ran = set()
	
	# -------------------------------------------------------------
	
	def should_run_task(self, task_name):
		# If history loading failed a full reprocessing is in order
		if not self.history.is_loaded():
			return
		
		# Command tasks should be run always (for now)
		task_config = self.tasks[task_name]
		if task_config.has_command():
			return True
		
		task_history = self.history.get_task(task_name)
		if task_history == None:
			return True
		
		if task_config.output_file != task_history['output_file']:
			return True
		
		if not os.path.exists(task_config.output_file):
			return True
		
		input_files_globbed = Utility.glob(task_config.input_files)
		
		for input_file in input_files_globbed:
			if input_file not in task_history['input_files']:
				return True
		
			file_modified_time = Utility.get_file_modify_utcdate(input_file)
			if task_history['last_processed'] < file_modified_time:
				return True
		
		for input_file in task_history['input_files']:
			if input_file not in input_files_globbed:
				return True
		
		return False
		
		
	def process_all_resources(self, force=False, minify=True):
		self.tasks_ran = set()
		
		print()
		for task_name, task_config in self.tasks.items():
			if task_name in self.tasks_ran:
				continue
			self.run_processor(task_name, force=force, minify=minify)
			print()
		
		self.history.save()
	
	# -------------------------------------------------------------------------
	
	def run_processor(self, task_name, force=False, minify=True) -> ProcessorResult:
		if task_name not in self.tasks:
			raise ResourceProcessorException(f"Processor task {task_name} is not defined.")
		
		self.tasks_ran.add(task_name)
		
		task_config = self.tasks[task_name]
		
		for depended_task_name in task_config.depends_on:
			if depended_task_name not in self.tasks:
				raise ResourceProcessorException(f"Task '{task_name}' depends on '{depended_task_name}' but no such task is defined.")
			
			if force or self.should_run_task(depended_task_name):
				print(f"{Fore.YELLOW}{Style.BRIGHT}Task '{task_name}' depends on '{depended_task_name}'  ...  {Style.RESET_ALL}", end='')
				
				result = self.run_processor(depended_task_name, minify=minify)
				if result == ProcessorResult.Failure:
					return ProcessorResult.Failure
				
				print()
				force = True
		
		print(f"{Fore.GREEN}{Style.BRIGHT}Processing task {task_name}...{Style.RESET_ALL}")
		
		final_result = ProcessorResult.NotProcessed
		
		# Pre-command task
		if task_config.has_pre_command():
			result = self.run_command_task(task_name, task_config.pre_command)
			if not result:
				print(f"    {Fore.RED}{Style.BRIGHT}Processing error! Aborting...{Style.RESET_ALL}")
				return ProcessorResult.Failure
			else:
				final_result = ProcessorResult.Success
				
		
		# File processing task
		if task_config.has_file_processor():
			if not force and not self.should_run_task(task_name):
				print(f"    {Fore.BLACK}{Style.BRIGHT}Input files unchanged                 ...  OK{Style.RESET_ALL}")
				
			else:
				result = self.run_file_processing_task(task_name, task_config, minify=minify)
				if not result:
					print(f"    {Fore.RED}{Style.BRIGHT}Processing error! Aborting...{Style.RESET_ALL}")
					return ProcessorResult.Failure
				else:	
					final_result = ProcessorResult.Success
		
		
		# Post-command task
		if task_config.has_post_command():
			result = self.run_command_task(task_name, task_config.post_command)
			if not result:
				print(f"    {Fore.RED}{Style.BRIGHT}Processing error! Aborting...{Style.RESET_ALL}")
				return ProcessorResult.Failure
				
			else:
				final_result = ProcessorResult.Success
				
				
		print(f"    {Fore.GREEN}{Style.BRIGHT}Processing complete!{Style.RESET_ALL}")
		return final_result
		
	
	def run_file_processing_task(self, task_name, task_config, minify):
		input_files_globbed = Utility.glob(task_config.input_files)
		
		task_config.processor_instance.process(
			input_files  = input_files_globbed,
			output_file  = task_config.output_file,
			minify       = minify
		)
		
		self.history.mark(task_name, input_files_globbed, task_config.output_file)
		print(f"    {Fore.GREEN}{Style.BRIGHT}File processing done!   {Fore.YELLOW}Output written to file:    {Fore.BLUE}{task_config.output_file}{Style.RESET_ALL}")
		return True
		
	
	def run_command_task(self, task_name, run_command):
		print(f"    {Fore.YELLOW}{Style.BRIGHT}Running command     {Fore.WHITE}: {Utility.concat(run_command, separator=' ')}{Style.RESET_ALL}")
		print()
		process = subprocess.Popen(run_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		
		with print_indent(4):
			while True:
				output = process.stdout.readline()
				if not output:
					break
				print(output.strip().decode())

				error = process.stderr.readline()
				if error:
					print(f"{Fore.RED}ERROR{Style.RESET_ALL} ", error.strip().decode())
		
		print()
		
		# Wait for the process to finish and check the return code
		return_code = process.wait()
		if return_code != 0:
			print(f"    {Fore.RED}{Style.BRIGHT}Process finished with errors  (error code {return_code}){Style.RESET_ALL}")
			return False
		
		return True
		
	
	def watch_changes(self, kill_duplicates = True, polling = False):
		from .FileProcessorWatcher import FileProcessorWatcher
		watcher = FileProcessorWatcher(self, kill_duplicates=kill_duplicates)
		watcher.start_watching(polling=polling)
